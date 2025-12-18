from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey
from sqlalchemy.exc import SQLAlchemyError

import datetime
import os

from ..database import db

from ..models import Certificate, CACertificate, CertificateSANs
from .fetchSSLController import parse_certificate


def issue_cacertificate(subject):
    try:
        # Gera chave privativa
        root_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )

        private_key_bytes = root_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        private_key_pem = private_key_bytes.decode("utf-8")

        # Monta atributos
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject.country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject.state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject.locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject.company),
            x509.NameAttribute(NameOID.COMMON_NAME, subject.commonName),
        ])
        # Gera e assina certificado
        root_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            root_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()),
            critical=False,
        ).sign(root_key, hashes.SHA256())

    except InvalidKey as e:
        return {"error": f"Erro na geração das chaves: {e}", "code": 400}
    except ValueError as e:
        return {"error": f"Campos não preenchidos corretamente: {e}", "code": 400}
    except Exception as e:
        return {"error": f"Operação não realizada: {e}", "code": 500}

    crt_pem = root_cert.public_bytes(
        encoding=serialization.Encoding.PEM
    ).decode("utf-8")

    # Envia para a função que irá pegar os dados de dentro do certificado
    parsed = parse_certificate(root_cert)

    cacertificate = CACertificate(
        common_name=parsed.get("common_name"),
        valid_from=parsed.get("not_before"),
        valid_to=parsed.get("not_after"),
        company=parsed.get("organization"),
        locality=parsed.get("locality"),
        state=parsed.get("state"),
        country=parsed.get("country"),
        key=private_key_pem,
        crt=crt_pem
    )

    try:
        db.session.add(cacertificate)
        db.session.commit()
    except Exception as e:
        return {"error": f"Erro ao salvar: {e}", "code": 400}

    return cacertificate.id


def issue_certificate(body):
    try:
        # Importa chave privativa da CA

        try:
            ca = db.session.get(CACertificate, body.ca)
        except SQLAlchemyError as error:
            return ({"error": "Database error"}), 500

        ca_key_string=ca.key
        ca_private_key = serialization.load_pem_private_key(
            ca_key_string.encode(),
            password=None,
        )
        # Importa o certificado CA
        ca_crt_string = ca.crt
        ca_cert = x509.load_pem_x509_certificate(ca_crt_string.encode(), default_backend())

        # Gera chave privativa
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        private_key_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        private_key_pem = private_key_bytes.decode("utf-8")

        # Monta o campo Subject(Assunto)
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, body.company),
                x509.NameAttribute(NameOID.COMMON_NAME, body.commonName),
            ]
        )
    except InvalidKey as e:
        return {"error": f"Erro na geração das chaves: {e}", "code": 400}
    except ValueError as e:
        return {"error": f"Campos não preenchidos corretamente: {e}", "code": 400}
    except Exception as e:
        return {"error": f"Operação não realizada: {e}", "code": 500}

    sans_raw = body.sans
    sans_list = [sans.strip() for sans in sans_raw.split(",") if sans.strip()]

    # Monta e assina certificado

    sans_names = [x509.DNSName(san) for san in sans_list]

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=90))
        .add_extension(x509.SubjectAlternativeName(sans_names),critical=False,)
        .sign(ca_private_key, hashes.SHA256())
    )
    crt_pem = cert.public_bytes(
        encoding=serialization.Encoding.PEM
    ).decode("utf-8")

    # Envia para a função que irá pegar os dados de dentro do certificado
    parsed = parse_certificate(cert)

    certificate = Certificate(
        common_name=parsed.get("common_name"),
        valid_from=parsed.get("not_before"),
        valid_to=parsed.get("not_after"),
        company=parsed.get("organization"),
        ca_id=body.ca,
        key=private_key_pem,
        crt=crt_pem
    )

    try:
        db.session.add(certificate)
        db.session.commit()
    except Exception as e:
        return {"error": f"Erro ao salvar: {e}", "code": 400}

    try:
        for san in sans_list:
            db.session.add(CertificateSANs(san=san, certificate_id=certificate.id))
        db.session.commit()
    except Exception as e:
        return {"error": f"Erro ao salvar: {e}", "code": 400}

    return certificate.id




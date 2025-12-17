from cryptography import x509
from cryptography.x509 import load_pem_x509_csr
from cryptography.x509.oid import NameOID
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidKey


def generate_request(subject):

    to_reply = {}
    if not subject.bits:
        # É dado o valor 2048 caso o usuário não preencha
        subject.bits=2048
    try:
        # Gera a chave privativa
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=subject.bits,
        )
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        to_reply["key"] = private_key_pem

        # Monta o subject
        request_builder = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject.company),
                x509.NameAttribute(NameOID.COMMON_NAME, subject.commonName),
            ])
        )
        # Assina a requisição
        csr = request_builder.sign(private_key, hashes.SHA256())
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)
        to_reply["csr"] = csr_pem
    except InvalidKey as e:
        return {"error": f"Erro na geração das chaves: {e}", "code": 400}
    except ValueError as e:
        return {"error": f"Campos não preenchidos corretamente: {e}", "code": 400}
    except Exception as e:
        return {"error": f"Operação não realizada: {e}", "code": 500}

    return to_reply


def process_decode(csr):
    try:
        formatted_csr = csr.csr.encode()

        req = load_pem_x509_csr(formatted_csr)

        # Pega o subject da requisição
        csr_data = {"subject": {
            attr.oid._name: attr.value for attr in req.subject
        }}

        # Pega o tamanho da chave pública
        pk = req.public_key()
        csr_data["public_key"] = {
            "key_size": pk.key_size,
        }

        # Pega o hash de assinatura
        csr_data["signature_hash"] = req.signature_hash_algorithm.name
    except InvalidKey as e:
        return {"error": f"Erro na geração das chaves: {e}", "code": 400}
    except ValueError as e:
        return {"error": f"Campos não preenchidos corretamente: {e}", "code": 400}
    except Exception as e:
        return {"error": f"Operação não realizada: {e}", "code": 500}

    return csr_data
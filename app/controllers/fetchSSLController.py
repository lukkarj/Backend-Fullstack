
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend

import socket
import ssl

def fetch_certificate(host, port):

    try:
        # Cria o context SSL
        context = ssl.create_default_context()

        # Cria a conexão
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as server_sock:
                # Carrega o certificado apresentado pelo servidor
                cert = server_sock.getpeercert(binary_form=True)
                # Converte para PEM
                pem_cert = ssl.DER_cert_to_PEM_cert(cert)
                # Chama função para pegar as informações do certificado
                cert_data = parse_certificate(pem_cert)
                return cert_data
    except socket.gaierror as e:
        return {"error": f"Common Name ou porta inválidos: {e}", "code": 400}
    except socket.timeout as e:
        return {"error": f"Gateway Timeout: {e}", "code":  504}
    except ConnectionRefusedError as e:
        return {"error": f"Conexão recusada pelo host: {e}", "code":  401}
    except Exception as error:
        return {"error": str(error), "code":  500}


def parse_certificate(cert):

    try:
        # Verifica codificação do certificado
        try:
            # Codifica caso receba um string do certificado
            certificate = x509.load_pem_x509_certificate(cert.encode(), default_backend())
        except:
            # Mantem o cert recebido caso já esteja codificado
            certificate = cert

        issuer = certificate.issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
        cn = certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

        try:
            organization = certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
        except:
            organization = " "
        try:
            locality = certificate.subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
        except:
            locality = " "
        try:
            state = certificate.subject.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value
        except:
            state = " "
        try:
            country = certificate.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
        except:
            country = " "

        info = {
            "common_name": cn,
            "organization": organization,
            "locality": locality,
            "state": state,
            "country": country,
            "issuer": issuer,
            "serial_number": certificate.serial_number,
            "not_before": certificate.not_valid_before,
            "not_after": certificate.not_valid_after,
            "signature_hash_algorithm": certificate.signature_hash_algorithm.name,
            "key_size": certificate.public_key().key_size
        }
        try:
            san_extension = certificate.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            sans_temp = san_extension.value.get_values_for_type(
                x509.DNSName
            )

            sans_list = [san for san in sans_temp]
            sans_str = '<br>'.join(sans_list)

            info["subject_alternative_names"] = sans_str

        except x509.ExtensionNotFound:
            info["subject_alternative_names"] = ""
        return info

    except ValueError as error:
        return {"error": str(error), "code":  500}

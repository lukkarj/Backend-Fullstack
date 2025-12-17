from flask import  redirect, jsonify
from flask_openapi3 import Tag
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.database import db

from app.schemas import *
from app.models import *
from app.controllers import *

# ======================================================
# TAGs
# ======================================================

home_tag = Tag(name="Documentação", description="Documentação: Scalar, RapiPDF, Swagger, Redoc, RapiDoc, Elements")
csr_tag = Tag(name="Requisições", description="Rotas de geração e decodificação de CSR")
certificate_tag = Tag(name="Certificados", description="Rotas de gerenciamento de certificados")


def routes(app):

    # ======================================================
    # Rota para documentação
    # ======================================================

    @app.get('/', tags=[home_tag])
    def home():
        return redirect('/openapi')

    # ======================================================
    # Rotas para buscar certificados
    # ======================================================

    @app.get("/listCACertificates", tags=[certificate_tag], responses={200: CACertificateList, 500: Error})
    def list_cacertificates():
    # Busca todas as CAs para popular a página
        try:
            cacertificates = CACertificate.query.all()
            if not cacertificates:
                # Retorna a lista vazia caso não tenha nenhum resultado
                return {"list": []}, 200
            else:
                cert_list = [cacertificate.format_CACertificate() for cacertificate in cacertificates]
        except SQLAlchemyError as error:
            return jsonify({"message": "Database error"}), 500
        return {
            "list": cert_list,
        }, 200


    @app.get("/listCertificates", tags=[certificate_tag], responses={200: CertificateList, 500: Error})
    # Busca todos os certificados emitidos para popular a página
    def list_certificates():
        try:
            certificates = Certificate.query.all()
            if not certificates:
                # Retorna a lista vazia caso não tenha nenhum resultado
                return {"list": []}, 200
            else:
                cert_list = [certificate.format_certificate() for certificate in certificates]
        except SQLAlchemyError as error:
            return jsonify({"message": "Database error"}), 500
        return {
            "list": cert_list,
        }, 200


    @app.get("/filteredList", tags=[certificate_tag], responses={200: CertificateList, 500: Error})
    def filter_certificates(query: CertificateFilter):
    # Filtra listagem por CA
        try:
            # Busca com base na CA selecionada
            certificates = (Certificate.query.filter(Certificate.ca_id == query.ca_id)).all()

            if not certificates:
                # Retorna a lista vazia caso não tenha nenhum resultado
                return {"list": []}, 200
            else:
                cert_list = [certificate.format_certificate() for certificate in certificates]
        except SQLAlchemyError as error:
            return jsonify({"message": "Database error"}), 500
        return {
            "list": cert_list,
        }, 200


    @app.get("/search", tags=[certificate_tag], responses={200: CertificateList, 500: Error})
    def search_certificates(query: CertificateSearch):
    # Busca string no Common Name e SANs do certificado
        try:
            certificates = Certificate.query.filter(
                or_(
                    func.lower(Certificate.common_name).contains(query.searchString.lower()),
                    Certificate.sans.any(
                        func.lower(CertificateSANs.san).contains(query.searchString.lower())
                    )
                )
            )
            if not certificates:
                # Retorna a lista vazia caso não tenha nenhum resultado
                return {"list": []}, 200
            else:
                cert_list = [certificate.format_certificate() for certificate in certificates]

        except SQLAlchemyError as error:
            return jsonify({"message": "Database error"}), 500
        return {
            "list": cert_list,
        }, 200

    # ======================================================
    # Rotas para geração de certificados
    # ======================================================

    @app.post("/generateCACertificate", tags=[certificate_tag], responses={200: CACertificateStruct, 400: Error, 500: Error})
    def generate_cacertificate(body: GenerateCACertificate):
        # Geração do certificado de CA

        reply=issue_cacertificate(body)
        if isinstance(reply, dict) and "error" in reply:
            return jsonify({"message": reply["error"]}), reply["code"]

        return {
            "name": reply,
        }, 200

    @app.post("/generateCertificate", tags=[certificate_tag], responses={200: CertificateStruct, 400: Error, 500: Error})
    def generate_certificate(body: GenerateCert):
    # Geração do certificados
        reply=issue_certificate(body)
        if isinstance(reply, dict) and "error" in reply:
            return jsonify({"message": reply["error"]}), reply["code"]
        return {
            "name": reply,
        }, 200


    @app.post("/renewCertificate", tags=[certificate_tag], responses={200: CertificateStruct, 400: Error, 500: Error})
    def renew_certificate(body: CertificateRenewal):
    # Geração de certificado de renovação com os mesmos dados do anterior
        try:
            to_renew = db.session.get(Certificate, body.id)
        except SQLAlchemyError as error:
            return jsonify({"error": "Database error"}), 500

        sans_list = [san.san for san in to_renew.sans]
        sans_str = ', '.join(sans_list)

        formatted = {
            "ca": to_renew.ca_id,
            "company": to_renew.company,
            "commonName": to_renew.common_name,
            "sans": sans_str
        }
        # Envia no formato chave=valor.
        built_body = GenerateCert(**formatted)

        reply=issue_certificate(built_body)

        if isinstance(reply, dict) and "error" in reply:
            return jsonify({"message": reply["error"]}), reply["code"]
        return {
            "name": reply,
        }, 200

    # ======================================================
    # Rota para excluir certificados
    # ======================================================

    @app.delete("/deleteCertificate", tags=[certificate_tag], responses={200: DeleteResult, 500: Error})
    def delete_certificate(body: CertificateDelete):
    # Deleta certificado selecionado
        try:
            to_delete=db.session.get(Certificate, body.id)
        except SQLAlchemyError as error:
            return jsonify({"message": "Database error"}), 500

        if to_delete:
            db.session.delete(to_delete)
            db.session.commit()
            return {
                "succeed": True,
            }, 200
        return jsonify({"message": "Database error"}), 500

    # ======================================================
    # Rota para geração de CSR
    # ======================================================

    @app.post("/generateCSR", tags=[csr_tag], responses={200: RequestOutput, 400: Error, 500: Error})
    def generate_csr(body: RequestSubject):
    # Gera par de chaves
        reply = generate_request(body)

        if isinstance(reply, dict) and "error" in reply:
            return jsonify({"message": reply["error"]}), reply["code"]

        formatted_csr = reply["csr"].decode().replace('\n', '<br>')
        formatted_key = reply["key"].decode().replace('\n', '<br>')

        return {
            "csr": formatted_csr,
            "key": formatted_key
        }, 200

    # ======================================================
    # Rota para decodificar CSR
    # ======================================================

    @app.post("/decodeCSR", tags=[csr_tag], responses={200: RequestDecodeOut, 400: Error, 500: Error})
    def decode_csr(body: RequestDecodeIn):
    # Decodificação do CSR
        csr_data = process_decode(body)

        if isinstance(csr_data, dict) and "error" in csr_data:
            return jsonify({"message": csr_data["error"]}), csr_data["code"]

        return {
            "csr_data": csr_data
        }, 200

    # ======================================================
    # Rota para discovery
    # ======================================================

    @app.get("/fetchSSL", tags=[certificate_tag], responses={200: CertificateStruct, 400: Error, 401: Error, 500: Error, 504: Error})
    def fetch_ssl(query: CertificateFetch):
    # Recebe url e porta e busca certificado utilizado
        common_name = query.commonName
        port = query.port

        data = fetch_certificate(common_name, port)
        if isinstance(data, dict) and "error" in data:
            return jsonify({"message": data["error"]}), data["code"]

        return {
            "ssl_data": data
        }, 200


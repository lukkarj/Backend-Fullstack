from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CertificateFetch(BaseModel):
    # Schema dos dados recebidos para fazer o discovery
    commonName: str
    port: int

class CertificateStruct(BaseModel):
    # Schema dos dados dos certificados
    issuer: str
    common_name: str
    valid_from: datetime
    valid_to: datetime
    company: Optional[str]
    sans: Optional[str]

class CertificateDelete(BaseModel):
    # Schema dos dados recebidos para deletar um certificado
    id: int

class CertificateRenewal(BaseModel):
    # Schema dos dados recebidos para renovar um certificado
    id: int

class DeleteResult(BaseModel):
    # Schema do resultado da remoção de um certificado
    succeed: bool

class CertificateList(BaseModel):
    # Schema da lista de certificados retornada
    certificates:List[CertificateStruct]

class GenerateCert(BaseModel):
    # Schema dos dados recebidos para gerar um certificado
    ca: int
    company: Optional[str]
    commonName: str
    sans: Optional[str]

class CertificateFilter(BaseModel):
    # Schema dos dados recebidos filtrar a lista de certificados
    ca_id: int

class CertificateSearch(BaseModel):
    # Schema dos dados recebidos buscar certificados
    searchString: str

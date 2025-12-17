from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CACertificateStruct(BaseModel):
    # Schema dos dados dos certificados de CA
    issuer: str
    common_name: str
    valid_from: datetime
    valid_to: datetime
    company: Optional[str]
    state: str
    locality: str
    country: str

class CACertificateDelete(BaseModel):
    # Schema dos dados recebidos para deletar um certificado de CA
    id: int

class CADeleteResult(BaseModel):
    # Schema do resultado da remoção de um certificado de CA
    succeed: bool

class CACertificateList(BaseModel):
    # Schema da lista de certificados de CA retornada
    certificates:List[CACertificateStruct]

class GenerateCACertificate(BaseModel):
    # Schema dos dados recebidos para gerar um certificado de CA
    company: str
    commonName: str
    locality: str
    state: str
    country: str
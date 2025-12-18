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

class CAKeysRequest(BaseModel):
    # Schema dos dados de entrada para fazer o download dos certificados de CA
    id: int

class CAKeysReply(BaseModel):
    # Schema dos dados de saída para fazer o download dos certificados de CA
    # O usuário não tem acesso à chave privativa dos certificados de CA, é enviado apenas o .crt
    crt: str

class CACertificateDelete(BaseModel):
    # Schema dos dados de entrada para deletar um certificado de CA
    id: int

class CADeleteResult(BaseModel):
    # Schema dos dados de saída da remoção de um certificado de CA
    succeed: bool

class CACertificateList(BaseModel):
    # Schema da lista de certificados de CA retornada
    certificates:List[CACertificateStruct]

class GenerateCACertificate(BaseModel):
    # Schema dos dados de entrada para gerar um certificado de CA
    company: str
    commonName: str
    locality: str
    state: str
    country: str
from pydantic import BaseModel
from typing import Optional


class RequestSubject(BaseModel):
    # Schema dos dados recebidos para gerar um CSR
    company: Optional[str]
    commonName: str
    bits: int

class RequestOutput(BaseModel):
    # Schema da saída da geração do CSR
    csr: str
    key: str

class RequestDecodeIn(BaseModel):
    # Schema dos dados recebidos para decodificar um CSR
    csr: str

class RequestDecodeSubject(BaseModel):
    # Schema do Subject do CSR decodificado
    commonName: str
    organizationName: Optional[str]
    stateOrProvinceName: Optional[str]
    localityName: Optional[str]
    countryName: Optional[str]

class RequestDecodeKey(BaseModel):
    # Schema representação do tamanho de chave
    key_size: int

class RequestDecodeScheme(BaseModel):
    # Schema montado do resoltado da decodigicação completa
    subject: RequestDecodeSubject
    public_key: RequestDecodeKey

class RequestDecodeOut(BaseModel):
    # Schema da resposta da decodificação de CSR
    csr_data: RequestDecodeScheme
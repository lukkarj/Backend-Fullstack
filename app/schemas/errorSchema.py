from pydantic import BaseModel

class Error(BaseModel):
    # Schema de como um erro será apresentado
    error: str
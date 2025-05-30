from pydantic import BaseModel

class EtasLoginRequest(BaseModel):
    id: str
    password: str
    
    
    
    
    
    
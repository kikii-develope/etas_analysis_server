from pydantic import BaseModel

class EtasLoginRequest(BaseModel):
    id: str
    password: str
    companyId: int
    yearMonth: str #yyyy-MM
    riskLevel: str # '양호', '보통', '주의', '위험', '매우위험'
    
    
    
    
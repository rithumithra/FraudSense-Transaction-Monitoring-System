from pydantic import BaseModel

class TransactionCreate(BaseModel):
    user_id: int
    amount: float
    merchant: str
    location: str
    device: str

class TransactionResponse(TransactionCreate):
    id: int
    risk_score: int
    is_fraud: bool
    fraud_reason: str

    class Config:
        from_attributes = True
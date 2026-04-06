from pydantic import BaseModel

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    type: str
    amount: float
    description: str | None

    class Config:
        from_attributes = True
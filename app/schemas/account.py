from pydantic import BaseModel

class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True
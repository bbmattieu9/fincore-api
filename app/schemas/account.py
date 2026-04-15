from pydantic import BaseModel

class AccountCreate(BaseModel):
    account_type: str
    balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True
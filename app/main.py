from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel, EmailStr


app = FastAPI()

users_db = []
accounts_db = []

# Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AccountCreate(BaseModel):
    user_id: int
    account_type: str
    balance: float = 0.0


# [GET] Root route
@app.get("/")
def root():
    return {"message": "FinCore API running..."}


# Helper func to find user
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


# [POST] - Create User
@app.post("/users")
def create_user(user: UserCreate):
    user_data = user.model_dump()
    user_data["id"] = len(users_db) + 1
    users_db.append(user_data)
    return user_data


# [GET] Users
@app.get("/users")
def get_users():
    return users_db

# [GET] User_by_id
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user



# Accounts Endpoints -----------------------------------------


# Helper func to generate AcctNo
def generate_account_number():
    return str(random.randint(1000000000, 9999999999))


# [POST] Create Account
@app.post("/accounts")
def create_account(account: AccountCreate):
    # Validate User Exist
    user = find_user(account.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    account_data = account.model_dump()
    account_data["id"] = len(accounts_db) + 1
    account_data["account_number"] = generate_account_number()
    accounts_db.append(account_data)
    return account_data


# [GET] Accounts
@app.get("/accounts")
def get_accounts():
    return accounts_db

# Helper func to find Account
def find_account(account_id: int):
    for account in accounts_db:
        if account["id"] == account_id:
            return account
    return None


# [GET] Account By ID
@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    account = find_account(account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account
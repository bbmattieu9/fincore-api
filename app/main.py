
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import random

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


app = FastAPI()


users_db = []
accounts_db = []
transactions_db = []

# ===== SCHEMAS =====
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AccountCreate(BaseModel):
    user_id: int
    account_type: str
    balance: float = 0.0


class TransactionCreate(BaseModel):
    account_id: int
    type: str
    amount: float
    description: str | None = None


# ========= HELPERS ===========
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None


def find_account(account_id: int):
    for account in accounts_db:
        if account["id"] == account_id:
            return account
    return None


def find_transaction(tx_id: int):
    for tx in transactions_db:
        if tx["id"] == tx_id:
            return tx
    return None


def generate_account_number():
    while True:
        account_number = str(random.randint(1000000000, 9999999999))
        if not any(acc["account_number"] == account_number for acc in accounts_db):
            return account_number


# ======== ROUTES ========

@app.get("/")
def root():
    return {"message": "FinCore API running..."}


# -------- USERS --------

@app.post("/users")
def create_user(user: UserCreate):
    user_data = user.model_dump()
    user_data["id"] = len(users_db) + 1
    user_data["password"] = hash_password(user.password)

    users_db.append(user_data)
    return user_data


@app.get("/users")
def get_users(limit: int = 10, skip: int = 0):
    return users_db[skip: skip + limit]


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# -------- AUTH --------

@app.post("/login")
def login(user: UserLogin):
    for db_user in users_db:
        if db_user["email"] == user.email:
            if verify_password(user.password, db_user["password"]):
                token = create_access_token({"sub": str(db_user["id"])})
                return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# -------- ACCOUNTS --------

@app.post("/accounts")
def create_account(account: AccountCreate, current_user: dict = Depends(get_current_user)):
    user = find_user(account.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    account_data = account.model_dump()
    account_data["id"] = len(accounts_db) + 1
    account_data["account_number"] = generate_account_number()

    accounts_db.append(account_data)
    return account_data


@app.get("/accounts")
def get_accounts(
        user_id: int | None = None,
        limit: inot = 10,
        skip: int = 0,
        current_user: dict = Depends(get_current_user)):
    filtered_accounts = accounts_db
    if user_id:
        filtered_accounts =[ acc for acc in accounts_db if acc["user_id"] == user_id]
    return filtered_accounts[skip: skip + limit]


@app.get("/accounts/{account_id}")
def get_account(account_id: int, current_user: dict = Depends(get_current_user)):
    account = find_account(account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


# -------- TRANSACTIONS --------

@app.post("/transactions")
def create_transaction(tx: TransactionCreate, current_user: dict = Depends(get_current_user)):
    account = find_account(tx.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if tx.type == "debit":
        if account["balance"] < tx.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        account["balance"] -= tx.amount

    elif tx.type == "credit":
        account["balance"] += tx.amount

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transaction type")

    tx_data = tx.model_dump()
    tx_data["id"] = len(transactions_db) + 1

    transactions_db.append(tx_data)
    return tx_data

@app.get("/transactions")
def get_transactions(
        account_id: int | None = None,
        limit: int = 10,
        skip: int = 0,
        current_user: dict = Depends(get_current_user)):
    filtered_transactions = transactions_db

    if account_id:
        filtered_transactions = [tx for tx in transactions_db if tx["account_id"] == account_id]
    return filtered_transactions[skip: skip + limit]



@app.get("/transactions/{tx_id}")
def get_transaction(tx_id: int, current_user: dict = Depends(get_current_user)):
    tx = find_transaction(tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx
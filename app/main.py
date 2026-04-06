from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
import random
from time import time

from app.core.db import engine, Base, get_db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction




from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# ================= IN-MEMORY (TEMPORARY) =================
# accounts_db = []
transactions_db = []
request_count = {}


# ================= ENUMS =================
class TransactionType(str, Enum):
    credit = "credit"
    debit = "debit"


# ================= SCHEMAS =================
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
    type: TransactionType
    amount: float = Field(gt=0)
    description: str | None = None


# ================= ROOT =================
@app.get("/")
def root():
    return {"message": "FinCore API running..."}


# ================= USERS (DB) =================

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }


@app.get("/users")
def get_users(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        for user in users
    ]


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }


# ================= AUTH (DB) =================

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": token, "token_type": "bearer"}


# ================= HELPERS (TEMP) =================

# def find_account(account_id: int):
#     for account in accounts_db:
#         if account["id"] == account_id:
#             return account
#     return None


def find_transaction(tx_id: int):
    for tx in transactions_db:
        if tx["id"] == tx_id:
            return tx
    return None


def generate_account_number(db: Session):
    while True:
        account_number = str(random.randint(1000000000, 9999999999))
        existing = db.query(Account).filter(
            Account.account_number == account_number
        ).first()

        if not existing:
            return account_number


# ================= ACCOUNTS (TEMP) =================


@app.post("/accounts")
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_account = Account(
        user_id=account.user_id,
        account_type=account.account_type,
        balance=account.balance,
        account_number=generate_account_number(db)
    )

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account

@app.get("/accounts")
def get_accounts(
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return db.query(Account)\
        .filter(Account.user_id == current_user)\
        .offset(skip)\
        .limit(limit)\
        .all()


@app.get("/accounts/{account_id}")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


# ================= TRANSACTIONS (TEMP) =================

@app.post("/transactions")
def create_transaction(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)):

    rate_limiter(current_user)


    account = db.query(Account).filter(
        Account.id == tx.account_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")


    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:

        if tx.type == "debit":
            if account.balance < tx.amount:
                raise HTTPException(status_code=400, detail="Insufficient balance")

            account.balance -= tx.amount

        elif tx.type == "credit":
            account.balance += tx.amount


        db_tx = Transaction(
            account_id=tx.account_id,
            type=tx.type.value,  # Enum → string
            amount=tx.amount,
            description=tx.description
        )

        db.add(db_tx)
        db.commit()
        db.refresh(db_tx)
        return db_tx

    except Exception:
        db.rollback()
        raise


@app.get("/transactions")
def get_transactions(
    account_id: int | None = None,
    limit: int = 10,
    skip: int = 0,
    current_user: int = Depends(get_current_user)
):
    filtered = transactions_db

    if account_id:
        filtered = [tx for tx in transactions_db if tx["account_id"] == account_id]

    return filtered[skip: skip + limit]


@app.get("/transactions/{tx_id}")
def get_transaction(tx_id: int, current_user: int = Depends(get_current_user)):
    tx = find_transaction(tx_id)

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return tx


# ================= RATE LIMIT =================

RATE_LIMIT = 5
WINDOW = 60


def rate_limiter(user_id: int):
    now = time()

    if user_id not in request_count:
        request_count[user_id] = []

    request_count[user_id] = [
        t for t in request_count[user_id] if now - t < WINDOW
    ]

    if len(request_count[user_id]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests")

    request_count[user_id].append(now)
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.core.db import engine, Base, get_db
from app.core.security import get_current_user

# Services
from app.services.user_service import (
    create_user_service,
    get_users_service,
    get_user_service,
)

from app.services.auth_service import login_service

from app.services.account_service import (
    create_account_service,
    get_accounts_service,
    get_account_service,
)

from app.services.transaction_service import (
    create_transaction_service,
    get_transactions_service,
    get_account_statement_service,
)

# Schemas
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse


app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# ================= ROOT =================

@app.get("/")
def root():
    return {"message": "FinCore API running..."}


# ================= USERS =================

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)


@app.get("/users", response_model=list[UserResponse])
def get_users(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    return get_users_service(db, limit, skip)


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_service(db, user_id)


# ================= AUTH =================

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_service(db, user)


# ================= ACCOUNTS =================

@app.post("/accounts", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return create_account_service(db, account, current_user)


@app.get("/accounts", response_model=list[AccountResponse])
def get_accounts(
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return get_accounts_service(db, current_user, skip, limit)


@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return get_account_service(db, account_id, current_user)


# ================= TRANSACTIONS =================

@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    tx: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return create_transaction_service(db, tx, current_user)


@app.get("/transactions", response_model=list[TransactionResponse])
def get_transactions(
    account_id: int | None = None,
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return get_transactions_service(db, current_user, account_id, limit, skip)


@app.get("/accounts/{account_id}/statement", response_model=list[TransactionResponse])
def get_account_statement(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    return get_account_statement_service(db, account_id, current_user)
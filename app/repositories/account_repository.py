from sqlalchemy.orm import Session
from app.models.account import Account
from typing import Literal


# ================= CREATE =================

def create_account(db: Session, account_data: dict) -> Account:
    account = Account(**account_data)
    db.add(account)
    return account


# ================= BASE QUERY =================

def get_accounts_query(db: Session):
    return db.query(Account)


# ================= FILTERS =================

def filter_by_user(query, user_id: int):
    return query.filter(Account.user_id == user_id)


# ================= PAGINATION =================

def apply_pagination(query, skip: int, limit: int):
    return query.offset(skip).limit(limit)


# ================= SINGLE =================

def get_account_by_id(db: Session, account_id: int) -> Account | None:
    return db.query(Account)\
        .filter(Account.id == account_id)\
        .first()


# ================= UPDATE =================

def update_account_balance(
    account: Account,
    amount: float,
    tx_type: Literal["credit", "debit"]
) -> Account:
    if tx_type == "debit":
        account.balance -= amount
    elif tx_type == "credit":
        account.balance += amount
    else:
        raise ValueError(f"Invalid transaction type: {tx_type}")

    return account
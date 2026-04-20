from sqlalchemy.orm import Session, Query
from typing import Optional, Literal
from app.models.account import Account


# ================= CREATE =================

def create_account(db: Session, account_data: dict) -> Account:
    account = Account(**account_data)
    db.add(account)
    return account


# ================= BASE QUERY =================

def get_accounts_query(db: Session) -> Query:
    return db.query(Account)


# ================= FILTERS =================

def filter_by_user(query: Query, user_id: int) -> Query:
    return query.filter(Account.user_id == user_id)


# ================= SORT (optional but consistent) =================

def apply_latest_sort(query: Query) -> Query:
    return query.order_by(Account.id.desc())


# ================= PAGINATION =================

def apply_pagination(query: Query, skip: int, limit: int) -> Query:
    return query.offset(skip).limit(limit)


# ================= SINGLE =================

def get_account_by_id(db: Session, account_id: int) -> Optional[Account]:
    return (
        get_accounts_query(db)
        .filter(Account.id == account_id)
        .first()
    )


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
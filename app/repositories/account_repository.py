from sqlalchemy.orm import Session
from app.models.account import Account


def create_account(db: Session, account_data: dict):
    account = Account(**account_data)
    db.add(account)
    return account


def get_account_by_id(db: Session, account_id: int):
    return db.query(Account).filter(Account.id == account_id).first()


def get_accounts_by_user(db: Session, user_id: int, skip: int, limit: int):
    return db.query(Account)\
        .filter(Account.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def update_account_balance(account, amount: float, tx_type: str):
    if tx_type == "debit":
        account.balance -= amount
    elif tx_type == "credit":
        account.balance += amount
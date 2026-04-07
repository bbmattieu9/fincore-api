from sqlalchemy.orm import Session
from app.models.account import Account

def create_account(db: Session, account_data: dict):
    account = Account(**account_data)
    db.add(account)
    return account

def get_accounts_by_user(db: Session, user_id: int, skip: int, limit: int):
    return db.query(Account)\
        .filter(Account.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
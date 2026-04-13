from sqlalchemy.orm import Session
from app.models.transaction import Transaction


# ================= CREATE =================

def create_transaction(db: Session, tx_data: dict):
    db_tx = Transaction(**tx_data)
    db.add(db_tx)
    return db_tx


# ================= READ =================

def get_transaction_by_id(db: Session, tx_id: int):
    return db.query(Transaction)\
        .filter(Transaction.id == tx_id)\
        .first()


def get_transactions_by_account(
    db: Session,
    account_id: int,
    skip: int,
    limit: int
):
    return db.query(Transaction)\
        .filter(Transaction.account_id == account_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_all_transactions(
    db: Session,
    skip: int,
    limit: int
):
    return db.query(Transaction)\
        .offset(skip)\
        .limit(limit)\
        .all()
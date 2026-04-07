from sqlalchemy.orm import Session
from app.models.transaction import Transaction


def create_transaction(db: Session, tx_data: dict):
    db_tx = Transaction(**tx_data)
    db.add(db_tx)
    return db_tx


def get_transactions_query(db: Session):
    return db.query(Transaction)
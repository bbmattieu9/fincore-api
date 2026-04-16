from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.transaction import Transaction


# CREATE stays the same
def create_transaction(db: Session, tx_data: dict):
    db_tx = Transaction(**tx_data)
    db.add(db_tx)
    return db_tx


# STEP 1: Base query
def get_transactions_query(db: Session):
    return db.query(Transaction)


# STEP 2: Filter
def filter_by_account(query, account_id: int):
    return query.filter(Transaction.account_id == account_id)


# STEP 3: Sorting
def apply_latest_sort(query):
    return query.order_by(desc(Transaction.id))


# STEP 4: Pagination
def apply_pagination(query, skip: int, limit: int):
    return query.offset(skip).limit(limit)


# STEP 5: Single
def get_transaction_by_id(db: Session, tx_id: int):
    return db.query(Transaction)\
        .filter(Transaction.id == tx_id)\
        .first()
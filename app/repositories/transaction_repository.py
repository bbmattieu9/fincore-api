from sqlalchemy.orm import Session, Query
from sqlalchemy import desc
from typing import Optional

from app.models.transaction import Transaction


# ================= CREATE =================

def create_transaction(db: Session, tx_data: dict) -> Transaction:
    db_tx = Transaction(**tx_data)
    db.add(db_tx)
    return db_tx


# ================= BASE QUERY =================

def get_transactions_query(db: Session) -> Query:
    return db.query(Transaction)


# ================= FILTER =================

def filter_by_account(query: Query, account_id: int) -> Query:
    return query.filter(Transaction.account_id == account_id)


# ================= SORT =================

def apply_latest_sort(query: Query) -> Query:
    return query.order_by(desc(Transaction.id))


# ================= PAGINATION =================

def apply_pagination(query: Query, skip: int, limit: int) -> Query:
    return query.offset(skip).limit(limit)


# ================= SINGLE =================

def get_transaction_by_id(db: Session, tx_id: int) -> Optional[Transaction]:
    return (
        get_transactions_query(db)
        .filter(Transaction.id == tx_id)
        .first()
    )
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.repositories.account_repository import get_account_by_id, update_account_balance
from app.repositories.transaction_repository import (
    create_transaction,
    get_transactions_query
)
from app.models.transaction import Transaction

from app.core.rate_limiter import rate_limiter


# ================= CREATE TRANSACTION =================

def create_transaction_service(db: Session, tx, current_user: int):
    # Rate limit
    rate_limiter(current_user)

    account = get_account_by_id(db, tx.account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    if tx.type.value == "debit" and account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        # Update balance
        update_account_balance(account, tx.amount, tx.type.value)

        # Create transaction
        db_tx = create_transaction(db, {
            "account_id": tx.account_id,
            "type": tx.type.value,
            "amount": tx.amount,
            "description": tx.description
        })

        db.commit()
        db.refresh(db_tx)

        return db_tx

    except Exception:
        db.rollback()
        raise


# ================= GET TRANSACTIONS =================

def get_transactions_service(
    db: Session,
    current_user: int,
    account_id: int | None,
    limit: int,
    skip: int
):
    query = get_transactions_query(db)

    if account_id:
        account = get_account_by_id(db, account_id)

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if account.user_id != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")

        query = query.filter_by(account_id=account_id)

    return query.order_by(desc(Transaction.id)).offset(skip).limit(limit).all()


# ================= ACCOUNT STATEMENT =================

def get_account_statement_service(
    db: Session,
    account_id: int,
    current_user: int
):
    account = get_account_by_id(db, account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = get_transactions_query(db).filter_by(account_id=account_id)

    return query.order_by(desc("id")).all()
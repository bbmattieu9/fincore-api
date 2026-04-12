from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.repositories.account_repository import (
    get_account_by_id,
    update_account_balance
)
from app.repositories.transaction_repository import (
    create_transaction,
    get_transactions_query
)
from app.models.transaction import Transaction
from app.utils.rate_limiter import rate_limiter


# ================= VALIDATION HELPER =================

def _validate_account_access(account, current_user: int):
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")


# ================= CREATE TRANSACTION =================

def create_transaction_service(db: Session, tx, current_user: int):
    # Rate limiting
    rate_limiter(current_user)

    account = get_account_by_id(db, tx.account_id)
    _validate_account_access(account, current_user)

    # Business rule: prevent overdraft
    if tx.type.value == "debit" and account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        # Update account balance
        update_account_balance(account, tx.amount, tx.type.value)

        # Persist transaction
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
        _validate_account_access(account, current_user)

        query = query.filter_by(account_id=account_id)

    return (
        query
        .order_by(desc(Transaction.id))  # latest first
        .offset(skip)
        .limit(limit)
        .all()
    )


# ================= ACCOUNT STATEMENT =================

def get_account_statement_service(
    db: Session,
    account_id: int,
    current_user: int
):
    account = get_account_by_id(db, account_id)
    _validate_account_access(account, current_user)

    return (
        get_transactions_query(db)
        .filter_by(account_id=account_id)
        .order_by(desc(Transaction.id))  # latest first
        .all()
    )
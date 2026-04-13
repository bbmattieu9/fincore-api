from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.repositories.account_repository import (
    get_account_by_id,
    update_account_balance
)
from app.repositories.transaction_repository import (
    create_transaction,
    get_transactions_by_account,
    get_all_transactions
)
from app.utils.rate_limiter import rate_limiter


# ================= VALIDATION HELPER =================

def _validate_account_access(account, current_user: int):
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")


# ================= CREATE TRANSACTION =================

def create_transaction_service(db: Session, tx, current_user: int):
    rate_limiter(current_user)

    account = get_account_by_id(db, tx.account_id)
    _validate_account_access(account, current_user)

    if tx.type.value == "debit" and account.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        update_account_balance(account, tx.amount, tx.type.value)

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
    if account_id:
        account = get_account_by_id(db, account_id)
        _validate_account_access(account, current_user)

        transactions = get_transactions_by_account(db, account_id, skip, limit)
    else:
        transactions = get_all_transactions(db, skip, limit)

    # Apply sorting (business rule)
    return sorted(transactions, key=lambda tx: tx.id, reverse=True)


# ================= ACCOUNT STATEMENT =================

def get_account_statement_service(
    db: Session,
    account_id: int,
    current_user: int
):
    account = get_account_by_id(db, account_id)
    _validate_account_access(account, current_user)

    transactions = get_transactions_by_account(db, account_id, 0, 1000)

    return sorted(transactions, key=lambda tx: tx.id, reverse=True)
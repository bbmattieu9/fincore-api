from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.account_repository import (
    get_account_by_id,
    update_account_balance
)
from app.repositories.transaction_repository import (
    create_transaction,
    get_transactions_query,
    filter_by_account,
    apply_latest_sort,
    apply_pagination
)
from app.utils.rate_limiter import rate_limiter


# ================= VALIDATION =================

def _validate_account_access(account: Account, current_user: int):
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    if account.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )


# ================= CREATE =================

def create_transaction_service(db: Session, tx, current_user: int):
    rate_limiter(current_user)

    account = get_account_by_id(db, tx.account_id)
    _validate_account_access(account, current_user)

    # Prevent overdraft
    if tx.type.value == "debit" and account.balance < tx.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )

    try:
        # Update balance
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

        query = filter_by_account(query, account_id)

    query = apply_latest_sort(query)
    query = apply_pagination(query, skip, limit)

    return query.all()


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
        .pipe(lambda q: filter_by_account(q, account_id))
        .pipe(apply_latest_sort)
        .all()
    )
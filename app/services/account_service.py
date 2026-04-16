from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.account import AccountCreate
from app.models.account import Account

from app.repositories.account_repository import (
    get_account_by_id,
    create_account,
    get_accounts_query,
    filter_by_user,
    apply_pagination
)

from app.utils.account_utils import generate_account_number


# ================= VALIDATION HELPER =================

def _validate_account_access(account: Account, current_user: dict):
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    if account.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )


# ================= CREATE ACCOUNT =================

def create_account_service(
    db: Session,
    account_data: AccountCreate,
    current_user: dict
) -> Account:

    account = create_account(db, {
        "user_id": current_user["id"],
        "account_type": account_data.account_type,
        "balance": account_data.balance,
        "account_number": generate_account_number(db)
    })

    db.commit()
    db.refresh(account)

    return account


# ================= GET USER ACCOUNTS =================

def get_accounts_service(
    db: Session,
    current_user: dict,
    skip: int,
    limit: int
):
    query = get_accounts_query(db)
    query = filter_by_user(query, current_user["id"])
    query = apply_pagination(query, skip, limit)

    return query.all()


# ================= GET SINGLE ACCOUNT =================

def get_account_service(
    db: Session,
    account_id: int,
    current_user: dict
) -> Account:
    account = get_account_by_id(db, account_id)
    _validate_account_access(account, current_user)

    return account
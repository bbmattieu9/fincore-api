from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.account_repository import (
    get_account_by_id,
    create_account,
    get_accounts_by_user
)

from app.utils.account_utils import generate_account_number
# from app.core.exceptions import not_found, forbidden

def create_account_service(db: Session, account_data, current_user: int):
    if account_data.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    account = create_account(db, {
        "user_id": account_data.user_id,
        "account_type": account_data.account_type,
        "balance": account_data.balance,
        "account_number": generate_account_number(db)
    })

    db.commit()
    db.refresh(account)
    return account


def get_accounts_service(db: Session, current_user: int, skip: int, limit: int):
    return get_accounts_by_user(db, current_user, skip, limit)


def get_account_service(db: Session, account_id: int, current_user: int):
    account = get_account_by_id(db, account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    return account
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.account_repository import (
    get_account_by_id,
    create_account,
    get_accounts_by_user
)


def create_account_service(
    db: Session,
    account_data,
    current_user: int,
    generate_account_number
):
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


def get_user_accounts_service(
    db: Session,
    current_user: int,
    skip: int,
    limit: int
):
    return get_accounts_by_user(db, current_user, skip, limit)
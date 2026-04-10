from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_users,
    get_user_by_id
)
from app.core.security import hash_password, verify_password, create_access_token


def create_user_service(db: Session, user):
    db_user = create_user(db, {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": "user"
    })

    db.commit()
    db.refresh(db_user)
    return db_user


def login_service(db: Session, user):
    db_user = get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token({"sub": str(db_user.id), "role": db_user.role })


def get_users_service(db: Session, limit: int, skip: int):
    return get_users(db, skip, limit)


def get_user_service(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_users,
    get_user_by_id
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


# ================= CREATE USER =================

def create_user_service(db: Session, user) -> User:
    # Prevent duplicate email
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_user = create_user(db, {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": "user"
    })

    db.commit()
    db.refresh(db_user)

    return db_user


# ================= LOGIN =================

def login_service(db: Session, user) -> dict:
    db_user = get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": str(db_user.id),
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ================= GET USERS =================

def get_users_service(db: Session, limit: int, skip: int) -> List[User]:
    return get_users(db, skip, limit)


# ================= GET SINGLE USER =================

def get_user_service(db: Session, user_id: int) -> User:
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
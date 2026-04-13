from sqlalchemy.orm import Session
from app.models.user import User


# ================= CREATE =================

def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    return user


# ================= READ =================

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User)\
        .filter(User.id == user_id)\
        .first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User)\
        .filter(User.email == email)\
        .first()


def get_users(db: Session, skip: int, limit: int) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()
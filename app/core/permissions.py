from fastapi import HTTPException, status, Depends
from typing import TypedDict

from app.core.security import get_current_user


class CurrentUser(TypedDict):
    id: int
    role: str


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: CurrentUser = Depends(get_current_user)):
        if (
            current_user["role"] not in allowed_roles
            and current_user["role"] != "admin"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user

    return role_checker
from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel, EmailStr


app = FastAPI()

users_db = []

# Schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# [GET] Root route
@app.get("/")
def root():
    return {"message": "FinCore API running..."}

# [POST] - Create User
@app.post("/users")
def create_user(user: UserCreate):
    user_data = user.model_dump()
    user_data["id"] = len(user_data) + 1
    users_db.append(user_data)
    return user_data

# [GET] Users
@app.get("/users")
def get_users():
    return users_db

# [GET] User_by_id
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Helper func to find user
def find_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    return None
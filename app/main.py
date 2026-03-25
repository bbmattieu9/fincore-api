from fastapi import FastAPI
from pydantic import BaseModel, EmailStr


app = FastAPI()

users = []

# Schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.get("/")
def root():
    return {"message": "FinCore API running..."}


@app.post("/users")
def create_user(user: UserCreate):
    users.append(user)
    return user


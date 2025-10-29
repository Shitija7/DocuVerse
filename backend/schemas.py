# schemas.py
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DocumentOut(BaseModel):
    id: int
    filename: str
    text_length: Optional[int] = None

    class Config:
        orm_mode = True

class QuestionRequest(BaseModel):
    question: str
    doc_id: Optional[int] = None
    top_k: int = 3

class QuestionAnswer(BaseModel):
    answer: str

class SummarizeRequest(BaseModel):
    doc_id: int

class SummarizeResponse(BaseModel):
    summary: str

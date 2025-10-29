from sqlalchemy.orm import Session
from models import User, Document
from datetime import datetime
from auth import get_password_hash, verify_password

def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)  # uses truncation
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_document(db: Session, filename: str, content: str, user_id: int):
    doc = Document(
        filename=filename,
        content=content,
        user_id=user_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db: Session, doc_id: int, user_id: int):
    return db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()

def get_user_documents(db: Session, user_id: int):
    return db.query(Document).filter(Document.user_id == user_id).all()
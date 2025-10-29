from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import create_user, authenticate_user, create_document, get_document
from auth import create_access_token
from schemas import UserCreate, UserLogin
import fitz
import os
import faiss
import numpy as np
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(" GOOGLE_API_KEY missing! Make sure it's in your .env file")

genai.configure(api_key=GOOGLE_API_KEY)
print(" Google Gemini API key loaded successfully!")

print("\n Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  ✓ {m.name}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
if openai_client:
    print(" OpenAI client initialized as backup")

app = FastAPI(title="RAG Chatbot Backend ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


vector_store = {}
dimension = 768  


def text_to_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split document text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    """Convert text chunks into embeddings using Google Gemini API."""
    embeddings = []
    for text in texts:
        try:
            # Use Google's embedding model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            embeddings.append(np.array(result['embedding'], dtype="float32"))
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")
    return np.vstack(embeddings)


def save_embeddings(doc_id: int, chunks: List[str], embeddings: np.ndarray):
    """Store embeddings in an in-memory FAISS index."""
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    vector_store[doc_id] = {"index": index, "chunks": chunks}


def retrieve_similar_chunks(doc_id: int, query: str, top_k: int = 3) -> List[str]:
    """Find top-k similar text chunks for a query."""
    if doc_id not in vector_store:
        return []

    query_emb = embed_texts([query])
    index = vector_store[doc_id]["index"]
    distances, indices = index.search(query_emb, top_k)
    chunks = vector_store[doc_id]["chunks"]

    return [chunks[i] for i in indices[0] if i < len(chunks)]



@app.get("/")
def root():
    return {"message": "RAG Chatbot Backend Running "}

#AUTH
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = create_user(db, user.username, user.password)
        return {"id": db_user.id, "username": db_user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username
    }

@app.post("/upload")
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process PDF or TXT files."""
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    contents = await file.read()
    text = ""

    if file.filename.endswith(".pdf"):
        try:
            with fitz.open(stream=contents, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF processing failed: {e}")
    elif file.filename.endswith(".txt"):
        text = contents.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in file")
    
    doc = create_document(db, file.filename, text, user_id)

    chunks = text_to_chunks(text)
    embeddings = embed_texts(chunks)
    save_embeddings(doc.id, chunks, embeddings)

    return {
        "message": "File uploaded and processed successfully ",
        "doc_id": doc.id,
        "filename": doc.filename,
        "chunks": len(chunks),
        "text_length": len(text)
    }


@app.post("/ask")
async def ask(
    question: str = Form(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Ask a question using RAG (Retrieval-Augmented Generation) from uploaded documents."""
    
    try:
        user_id = int(user_id)
    except ValueError:
        return {"answer": "Invalid user_id format"}
    
    from crud import get_user_documents
    documents = get_user_documents(db, user_id)
    
    if not documents or not vector_store:
        return {"answer": "No documents uploaded yet. Please upload a document first."}
    
    all_chunks = []
    for doc in documents:
        if doc.id in vector_store:
            chunks = vector_store[doc.id]["chunks"]
            if chunks:
                relevant = [chunk for chunk in chunks if any(word.lower() in chunk.lower() 
                           for word in question.split() if len(word) > 3)]
                if relevant:
                    all_chunks.extend(relevant[:2])  
    
    if all_chunks:
        context = "\n\n".join(all_chunks[:5])  
        prompt = f"""Based on the following document content, answer the question.

Document Content:
{context}

Question: {question}

Provide a detailed answer based on the document content above."""
    else:
        prompt = f"Answer the following question: {question}"

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        return {
            "answer": response.text.strip()
        }
    except Exception as e1:
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return {
                    "answer": response.choices[0].message.content
                }
            except Exception as e2:
                return {"answer": f"Error: Gemini failed ({str(e1)}), OpenAI failed ({str(e2)})"}
        else:
            return {"answer": f"Error: {str(e1)}"}


@app.post("/summarize")
async def summarize_document(
    user_id: str = Form(...),
    doc_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Generate AI summary of a specific uploaded document."""
    
    try:
        user_id = int(user_id)
        doc_id = int(doc_id)
    except ValueError:
        return {"summary": "Invalid user_id or doc_id format"}
    
    doc = get_document(db, doc_id, user_id)
    
    if not doc:
        return {"summary": "Document not found or doesn't belong to you."}
    
    if not doc.content:
        return {"summary": "No content found in this document."}
    
    prompt = f"""Summarize the following document into a concise, informative summary.

Document: {doc.filename}

Content:
{doc.content}

Provide a comprehensive summary that covers the main points and key information."""
    
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        return {
            "summary": response.text.strip(),
            "filename": doc.filename
        }
    except Exception as e1:
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return {
                    "summary": response.choices[0].message.content,
                    "filename": doc.filename
                }
            except Exception as e2:
                return {"summary": f"Error: Gemini failed ({str(e1)}), OpenAI failed ({str(e2)})"}
        else:
            return {"summary": f"Error: {str(e1)}"}


@app.get("/documents/{user_id}")
async def get_user_docs(user_id: str, db: Session = Depends(get_db)):
    """Get all documents for a user."""
    try:
        user_id = int(user_id)
    except ValueError:
        return {"documents": []}
    
    from crud import get_user_documents
    documents = get_user_documents(db, user_id)
    
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename
            }
            for doc in documents
        ]
    }

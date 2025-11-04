# main.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud import create_user, authenticate_user, create_document, get_document, get_user_documents
from auth import create_access_token
from schemas import UserCreate, UserLogin
from database import supabase
import fitz
import os
import faiss
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List

# ==============================
# Load environment variables
# ==============================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("❌ GOOGLE_API_KEY missing! Add it to your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)
print("✅ Google Gemini API key loaded successfully!")

# ==============================
# App setup
# ==============================
app = FastAPI(title="RAG Chatbot Backend (Supabase Integrated)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# FAISS in-memory store
# ==============================
vector_store = {}
dimension = 768  # embedding vector size


# ==============================
# Helper Functions
# ==============================
def text_to_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    embeddings = []
    for text in texts:
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            embeddings.append(np.array(result['embedding'], dtype="float32"))
        except Exception as e:
            raise RuntimeError(f"Embedding failed: {e}")
    return np.vstack(embeddings)


def save_embeddings(doc_id: int, chunks: List[str], embeddings: np.ndarray):
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    vector_store[doc_id] = {"index": index, "chunks": chunks}


# ==============================
# API Endpoints
# ==============================

@app.get("/")
def root():
    print("✅ Root endpoint accessed.")
    return {"message": "🚀 RAG Chatbot Backend Running with Supabase!"}


# ---------- USER SIGNUP ----------
@app.post("/signup")
def signup(user: UserCreate):
    print("\n=========================")
    print(f"📩 SIGNUP REQUEST for username: {user.username}")
    print("=========================")
    try:
        db_user = create_user(supabase, user.username, user.password)
        print(f"✅ SIGNUP SUCCESS: {db_user}")
        return {"id": db_user["id"], "username": db_user["username"]}
    except ValueError as e:
        print(f"❌ SIGNUP ERROR: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ UNEXPECTED SIGNUP ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------- USER LOGIN ----------
@app.post("/login")
def login(user: UserLogin):
    print(f"\n🔑 LOGIN REQUEST for username: {user.username}")
    db_user = authenticate_user(supabase, user.username, user.password)
    if not db_user:
        print("❌ LOGIN FAILED: Invalid credentials")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": db_user["username"]})
    print(f"✅ LOGIN SUCCESS for user_id={db_user['id']}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user["id"],
        "username": db_user["username"]
    }


# ---------- DOCUMENT UPLOAD ----------
@app.post("/upload")
async def upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    print(f"\n📤 Upload request from user_id={user_id}, file={file.filename}")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    contents = await file.read()
    text = ""

    if file.filename.endswith(".pdf"):
        with fitz.open(stream=contents, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    elif file.filename.endswith(".txt"):
        text = contents.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported")

    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in file")

    print(f"🧩 Extracted text length: {len(text)} chars")
    
    try:
        doc = create_document(supabase, file.filename, text, user_id)
        print(f"✅ Document stored in Supabase: {doc}")
    except Exception as e:
        print(f"❌ FAILED to save document to Supabase: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")

    chunks = text_to_chunks(text)
    embeddings = embed_texts(chunks)
    save_embeddings(doc["id"], chunks, embeddings)
    print(f"💾 Stored {len(chunks)} chunks in FAISS memory.")

    return {
        "message": "✅ File uploaded and processed successfully!",
        "doc_id": doc["id"],
        "filename": doc["filename"],
        "chunks": len(chunks),
        "text_length": len(text)
    }


# ---------- ASK ----------
@app.post("/ask")
async def ask(question: str = Form(...), user_id: str = Form(...)):
    print(f"\n❓ ASK REQUEST: user_id={user_id}, question='{question}'")
    try:
        user_id = int(user_id)
    except ValueError:
        return {"answer": "Invalid user_id format"}

    documents = get_user_documents(supabase, user_id)
    print(f"🗂 Found {len(documents)} documents for this user")

    if not documents or not vector_store:
        return {"answer": "No documents uploaded yet."}

    all_chunks = []
    for doc in documents:
        if doc["id"] in vector_store:
            chunks = vector_store[doc["id"]]["chunks"]
            relevant = [chunk for chunk in chunks if any(word.lower() in chunk.lower()
                           for word in question.split() if len(word) > 3)]
            if relevant:
                all_chunks.extend(relevant[:2])

    if all_chunks:
        context = "\n\n".join(all_chunks[:5])
        prompt = f"""Based on the document, answer this:

{context}

Question: {question}"""
    else:
        prompt = f"Answer generally: {question}"

    print("🤖 Generating response from Gemini...")
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    print("✅ Gemini response ready.")
    return {"answer": response.text.strip()}


# ---------- GET DOCUMENTS ----------
@app.get("/documents/{user_id}")
async def get_user_docs(user_id: str):
    print(f"\n📂 Fetching documents for user_id={user_id}")
    try:
        user_id = int(user_id)
    except ValueError:
        return {"documents": []}

    documents = get_user_documents(supabase, user_id)
    print(f"✅ Retrieved {len(documents)} document(s)")
    return {
        "documents": [{"id": d["id"], "filename": d["filename"]} for d in documents]
    }

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud import create_user, authenticate_user, create_document, get_user_documents
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


app = FastAPI(title="RAG Chatbot Backend (Supabase Integrated)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions

def text_to_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split long text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    """Generate embeddings for a list of text chunks."""
    embeddings = []
    for text in texts:
        try:
            result = genai.embed_content(model="models/text-embedding-004", content=text)
            emb = np.array(result["embedding"], dtype="float32")
            embeddings.append(emb)
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            raise RuntimeError(f"Embedding failed: {e}")
    return np.vstack(embeddings)


def save_embeddings(doc_id: int, chunks: list[str], embeddings: np.ndarray):
    from database import supabase
    print(f"💾 Preparing to insert {len(chunks)} embeddings for doc_id={doc_id} ...")

    data_to_insert = []
    for chunk, emb in zip(chunks, embeddings):
        # Convert numpy vector to Postgres vector literal
        emb_literal = "[" + ",".join(map(str, emb.tolist())) + "]"
        data_to_insert.append({
            "doc_id": doc_id,
            "chunk_text": chunk,
            "embedding": emb_literal  
        })

    try:
        supabase.table("document_embeddings").insert(data_to_insert).execute()
        print(f"✅ Saved {len(chunks)} embeddings to Supabase for doc_id={doc_id}")
    except Exception as e:
        print(f"❌ Failed to save embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))



def load_faiss_index_from_supabase(doc_id: int):
    response = supabase.table("document_embeddings").select("chunk_text, embedding").eq("doc_id", doc_id).execute()
    data = response.data

    if not data:
        print(f"⚠️ No embeddings found for doc_id={doc_id}")
        return None

    chunks = []
    embeddings = []

    for row in data:
        chunks.append(row["chunk_text"])
        emb = row["embedding"]

        # ✅ Convert string to list of floats if necessary
        if isinstance(emb, str):
            emb = emb.strip()
            if emb.startswith("[") and emb.endswith("]"):
                emb = [float(x) for x in emb[1:-1].split(",") if x.strip()]
            else:
                emb = json.loads(emb)

        embeddings.append(emb)

    embeddings = np.array(embeddings, dtype=np.float32)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    print(f"✅ Loaded FAISS index with {len(chunks)} vectors for doc_id={doc_id}")
    return {"index": index, "chunks": chunks}


# ==============================
# API Endpoints
# ==============================

@app.get("/")
def root():
    print("🌐 Root endpoint accessed.")
    return {"message": "RAG Chatbot Backend Running with Supabase!"}


# ---------- USER SIGNUP ----------
@app.post("/signup")
def signup(user: UserCreate):
    print(f"\n📩 SIGNUP REQUEST for username: {user.username}")
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
        print(f"❌ FAILED to save document metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")

    # Generate embeddings and save
    chunks = text_to_chunks(text)
    embeddings = embed_texts(chunks)
    save_embeddings(doc["id"], chunks, embeddings)

    return {
        "message": "File uploaded and processed successfully!",
        "doc_id": doc["id"],
        "filename": doc["filename"],
        "chunks": len(chunks),
        "text_length": len(text)
    }


# ---------- ASK QUESTION ----------
@app.post("/ask")
async def ask(question: str = Form(...), user_id: str = Form(...)):
    print(f"\n❓ ASK REQUEST: user_id={user_id}, question='{question}'")
    try:
        user_id = int(user_id)
    except ValueError:
        return {"answer": "Invalid user_id format"}

    documents = get_user_documents(supabase, user_id)
    print(f"🗂 Found {len(documents)} documents for this user")

    if not documents:
        return {"answer": "No documents found. Please upload first."}

    all_chunks = []

    for doc in documents:
        print(f"📥 Loading FAISS index for doc_id={doc['id']}...")
        try:
            vector_data = load_faiss_index_from_supabase(doc["id"])
        except Exception as e:
            print(f"❌ Error loading embeddings for doc_id={doc['id']}: {e}")
            continue

        if not vector_data:
            continue

        index = vector_data["index"]
        chunks = vector_data["chunks"]

        query_emb = embed_texts([question])
        distances, indices = index.search(query_emb, 3)

        for i in indices[0]:
            if i < len(chunks):
                all_chunks.append(chunks[i])

    if not all_chunks:
        return {"answer": "No relevant content found in documents."}

    context = "\n\n".join(all_chunks[:5])
    prompt = f"""Based on the following document content, answer clearly.

Document Content:
{context}

Question: {question}
"""

    print("🤖 Generating response using Gemini...")
    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        response = model.generate_content(prompt)
        print("✅ Gemini response ready.")
        return {"answer": response.text.strip()}
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return {"answer": "Sorry, I couldn’t generate a response right now."}


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
    return {"documents": [{"id": d["id"], "filename": d["filename"]} for d in documents]}

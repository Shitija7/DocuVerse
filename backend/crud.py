# crud.py
from supabase import Client
from auth import get_password_hash, verify_password

def create_user(supabase, username: str, password: str):
    """Create a new user in Supabase"""
    print(f"🧾 Creating user '{username}' in Supabase...")

    hashed = get_password_hash(password)
    try:
        # Check if user already exists
        existing = supabase.table("users").select("id").eq("username", username).execute()
        if existing.data:
            print(f"⚠️ User '{username}' already exists in Supabase.")
            raise ValueError("Username already exists")

        # Insert new user
        response = supabase.table("users").insert({
            "username": username,
            "password": hashed
        }).execute()

        if not response.data:
            print(f"❌ Insert failed — no data returned from Supabase.")
            raise ValueError("Failed to create user in Supabase")

        user = response.data[0]
        print(f"✅ User created successfully in Supabase: {user}")
        return user

    except Exception as e:
        print(f"❌ Error creating user in Supabase: {e}")
        raise


def authenticate_user(supabase: Client, username: str, password: str):
    """Validate username and password."""
    response = supabase.table("users").select("*").eq("username", username).execute()
    if not response.data:
        return None
    user = response.data[0]
    if verify_password(password, user["password"]):
        return user
    return None

def create_document(supabase: Client, filename: str, content: str, user_id: int):
    """Insert a new document."""
    print(f"📝 Attempting to insert document: filename={filename}, user_id={user_id}, content_length={len(content)}")
    try:
        response = supabase.table("documents").insert({
            "filename": filename,
            "content": content,
            "user_id": user_id
        }).execute()
        
        if not response.data:
            print(f"❌ Insert failed — no data returned from Supabase.")
            print(f"Response: {response}")
            raise ValueError("Failed to create document in Supabase: No data returned")
        
        print(f"✅ Document created successfully in Supabase: {response.data[0]}")
        return response.data[0]
    except Exception as e:
        print(f"❌ Error creating document in Supabase: {type(e).__name__}: {e}")
        raise

def get_document(supabase: Client, doc_id: int, user_id: int):
    """Fetch a document by id and user."""
    response = supabase.table("documents").select("*").eq("id", doc_id).eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

def get_user_documents(supabase: Client, user_id: int):
    """Fetch all documents for a user."""
    response = supabase.table("documents").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data or []

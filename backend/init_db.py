#!/usr/bin/env python3
"""Initialize or reset the database"""
import os
from database import engine, SessionLocal
from models import Base, User
from auth import get_password_hash

# Delete existing database files if they exist
db_files = ['./test.db', './rag_chatbot.db']
for db_file in db_files:
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✓ Deleted {db_file}")
        except PermissionError:
            print(f"⚠ Skipping {db_file} (database is in use. Stop the backend and delete manually if needed)")
        except Exception as e:
            print(f"⚠ Error deleting {db_file}: {e}")

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Database tables created")

# Create a test user (optional)
db = SessionLocal()
try:
    # Check if test user exists
    test_user = db.query(User).filter(User.username == "admin").first()
    if not test_user:
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        print("✓ Test user created (username: admin, password: admin123)")
    else:
        print("ℹ Test user already exists")
except Exception as e:
    print(f"✗ Error creating test user: {e}")
finally:
    db.close()

print("\n🎉 Database initialized successfully!")
print("\nYou can now start the backend with: uvicorn main:app --reload")


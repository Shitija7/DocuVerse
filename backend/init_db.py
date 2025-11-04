#!/usr/bin/env python3
"""Initialize or verify Supabase database connection and create test user"""
import os
import logging
from database import get_db
from auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Verifying Supabase database connection...")
try:
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("SELECT 1")
    logger.info("✓ Successfully connected to Supabase database")
except Exception as e:
    logger.error(f"✗ Failed to connect to Supabase: {e}")
    logger.error("Make sure SUPABASE_URL is set correctly in your .env file")
    raise



# Create a test user (optional)
logger.info("Checking for test user...")
try:
    with get_db() as db:
        with db.cursor() as cur:
            # Check if test user exists
            cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
            test_user = cur.fetchone()
            
            if not test_user:
                # Create test user
                hashed_password = get_password_hash("admin123")
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
                    ("admin", hashed_password)
                )
                user_id = cur.fetchone()[0]
                db.commit()
                logger.info(f"✓ Test user created (username: admin, password: admin123, ID: {user_id})")
            else:
                logger.info("ℹ Test user already exists")
except Exception as e:
    logger.error(f"✗ Error creating test user: {e}")
# 🔄 How to Reset the Database

The database needs to be reinitialized after updating the models. Follow these steps:

## Steps to Reset:

1. **Stop the backend server** (if running)
   - Find the terminal where `uvicorn main:app --reload` is running
   - Press `Ctrl+C` to stop it

2. **Delete the old database files**:
   ```bash
   # In the backend folder
   rm test.db rag_chatbot.db
   # Or manually delete these files through File Explorer
   ```

3. **Run the init script**:
   ```bash
   python init_db.py
   ```

4. **Start the backend again**:
   ```bash
   uvicorn main:app --reload
   ```

## Quick Command (after stopping backend):

```bash
# Windows
del test.db rag_chatbot.db
python init_db.py

# Mac/Linux
rm -f test.db rag_chatbot.db
python init_db.py
```

## Alternative: Just Delete and Restart

If you don't want to run the init script, you can:
1. Stop the backend
2. Delete `test.db` and `rag_chatbot.db` files
3. Start the backend - it will create new tables automatically with the correct schema

The init script just adds a test user (admin/admin123) but is optional.


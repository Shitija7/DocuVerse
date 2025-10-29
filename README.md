# DocuVerse - RAG Chatbot Platform
##  Features

-  User Authentication - Secure login/signup with JWT tokens
-  Document Upload - Support for PDF and TXT files
-  AI Chat Interface - Ask questions about your documents
-  Modern UI- Beautiful React + Vite frontend
-  Summarize Tab - Placeholder for document summarization
-  RAG Read - Backend structure ready for vector search integration

## Project Structure

```
DocuVerse/
├── backend/          # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── auth.py       # JWT authentication
│   ├── models.py     # Database models
│   ├── crud.py       # Database operations
│   └── ...
└── frontend/         # React + Vite frontend
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Login.jsx
    │   │   ├── Dashboard.jsx
    │   │   ├── FileUpload.jsx
    │   │   ├── Chat.jsx
    │   │   └── Summarize.jsx
    │   └── 
    └── 



### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `.\venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the `backend` directory:
```env
Google ai studio=your_Google_ai_api_key_here
JWT_SECRET=your_super_secret_jwt_key_here
```

6. Run the backend:
```bash
uvicorn main:app --reload
```

The backend will be running on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be running on `http://localhost:5173`

##  Usage

1. **Sign Up** - Create a new account
2. **Upload Documents** - Upload PDF or TXT files
3. **Ask Questions** - Chat with your documents in the Chat tab
4. **Summarize** - Generate summaries

##  API Endpoints

- `POST /signup` - Create new user
- `POST /login` - Login and get JWT token
- `POST /upload` - Upload document
- `POST /ask` - Ask a question

Tech Stack

### Backend
- FastAPI
- SQLAlchemy (SQLite)
- JWT authentication
- Google AI studio API

### Frontend
- React 18
- Vite
- Axios
- Modern CSS with gradients

##  Authentication

The app uses JWT-based authentication. Users must sign up or login to:
- Upload documents
- Ask questions
- Access their data






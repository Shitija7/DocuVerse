Here’s a clean, professional, and human-readable version of your **README** — rewritten for clarity, tone, and readability, without emojis:

---

# DocuVerse Frontend

The **DocuVerse Frontend** is a modern web interface built with **React** and **Vite**, designed to interact seamlessly with the DocuVerse RAG Chatbot platform. It provides an intuitive user experience for uploading documents, chatting with AI, and managing authentication.

---

## Features

### Authentication

* User registration and login functionality
* Secure JWT-based authentication
* Persistent sessions using `localStorage`

### Document Upload

* Drag-and-drop upload functionality
* Supports both PDF and TXT file formats
* Real-time feedback during file uploads

### Chat Interface

* Ask questions directly about your uploaded documents
* Displays complete chat history (user and AI responses)
* Includes loading states and error handling for better UX

### Summarize Tab

* Reserved for upcoming document summarization functionality

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will run locally at:
`http://localhost:5173`

### 3. Build for Production

```bash
npm run build
```

---

## Project Structure

```
src/
├── main.jsx           
├── App.jsx            
├── api.js             
├── components/
│   ├── Login.jsx      
│   ├── Dashboard.jsx  
│   ├── FileUpload.jsx 
│   ├── Chat.jsx      
│   └── Summarize.jsx  

## Backend Integration

This frontend communicates with a FastAPI backend running at:
`http://localhost:8000`

Ensure the backend is active before starting the frontend.

### API Endpoints

API Endpoints Used:-
POST /signup – Registers a new user account.

POST /login – Authenticates the user and returns a JWT token.

POST /upload – Uploads a document file (supports PDF and TXT formats).

POST /ask – Allows the user to ask questions related to their uploaded documents.


## UI/UX Highlights

* Modern, clean, and consistent visual design
* Fully responsive layout for all screen sizes

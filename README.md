# 🥦 NutriRAG: A RAG-powered Nutrition Assistant

NutriRAG is a Retrieval-Augmented Generation (RAG) application built for CS6120, providing nutrition and recipe recommendations through an interactive chatbot. It uses FastAPI for the backend, Streamlit for the frontend, and FAISS for semantic search over curated recipe data.

---

## 🚀 Features

- **Conversational Assistant** with memory and history
- **FAISS-based Retrieval** over indexed recipe data
- **LangChain Pipelines** with prompt chaining (intent → rewrite → answer)
- **Google Cloud Compatible** deployment with Cloud Run and GCS
- **Docker & Docker Compose** setup for local and cloud environments

---

## 📂 Project Structure

```
CS6120-NutriRAG/
├── app/                         # FastAPI backend
│   ├── main.py                  # Entry point for backend
│   ├── routes.py                # API route definitions
│   ├── model_loader.py          # LLM & retriever loading logic
│   ├── rag_chain.py             # RAG logic: preprocess → retrieve → generate
│   ├── prompts.py               # Prompt templates for LLM chains
│   ├── schemas.py               # Pydantic models for request/response
│   ├── requirements.txt         # Backend dependencies
│   └── Dockerfile               # Backend Docker image
│
├── frontend/                    # Streamlit UI frontend
│   ├── app.py                   # Streamlit UI entry point
│   ├── requirements.txt         # Frontend dependencies
│   └── Dockerfile               # Frontend Docker image
│
├── data/index/langchain_faiss/ # FAISS index + metadata (not uploaded to GitHub)
│   ├── index.faiss
│   └── index.pkl
│
├── docker-compose.yml          # Compose both frontend & backend
├── README.md
```

---

## 🧪 Local Development

### 1. Install Docker Desktop and Clone Project

```bash
git clone https://github.com/huyiling521/CS6120-NutriRAG.git
or
git clone git@github.com:huyiling521/CS6120-NutriRAG.git

cd CS6120-NutriRAG
```

### 2. Setup `.env` Files

- `app/.env`:
  ```
  OPENAI_API_KEY=YOUR-OPENAI-API-KEY
  IS_CLOUD_ENV=false
  ```

- `frontend/.env`:
  ```
  POST_BASE_URL=http://app:8000
  ```

### 3. Build & Run Locally

```bash
docker-compose up --build
```

- Frontend runs at: http://0.0.0.0:8501
- Backend API runs at: http://0.0.0.0:8000

---


## 📎 Notes

- If FAISS files are missing locally, backend will auto-download from Drive or GCS
- `docker-compose` sets up network linking so `http://app:8000` works in frontend

---

## 👥 Team

- Yiling Hu
- Liu Yang
- Dongyin Li
- Junhui Sun

---

## 🧠 Powered By

- LangChain
- OpenAI
- HuggingFace Embeddings
- FAISS
- Streamlit
- FastAPI
- Google Cloud Run
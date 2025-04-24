# 🥦 NutriRAG: A RAG-Powered Nutrition Assistant

**NutriRAG** is a Retrieval-Augmented Generation (RAG) system designed to help users get personalized meal plans, recipe suggestions, and nutritional guidance powered by a large language model (LLM). Users can ask for protein-rich meals, healthy substitutes, or low-calorie recipes, and the system retrieves real-world recipe data and generates markdown-based meal plans.

---

## 🗂️ Project Structure

```plaintext
CS6120-NutriRAG/
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── model_loader.py        # RAG component loader (LLM, retriever, chains)
│   ├── prompts.py             # Prompt templates for each stage of the pipeline
│   ├── rag_chain.py           # Core RAG pipeline implementation
│   ├── routes.py              # FastAPI route definitions
│   ├── schemas.py             # Pydantic schemas for request/response models
│
├── data/
│   ├── longchain_convert.py   # Helper script to build FAISS index from metadata
│   └── index/
│       ├── combined_metadata.json      # Source metadata for vector index
│       └── langchain_faiss/
│           ├── index.faiss            # FAISS vector store
│           └── index.pkl              # Index mapping metadata
│
├── frontend/
│   ├── app.py                # Streamlit frontend for chat-based interface
│   └── .env                  # Frontend config (e.g., BACKEND_URL)
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project description and setup guide
└── .env                      # Backend config (e.g., OPENAI_API_KEY)
```

---

## ⚙️ Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/CS6120-NutriRAG.git
cd CS6120-NutriRAG
```

### 2. Install Dependencies and download data files

```bash
pip install -r requirements.txt
cd ./CS6120-NutriRAG/data/
gdown 1_ouVNYI2SPzjhLY4iQ18Gjy-U7XWCpb4
gdown --folder 1fgvui1M1kAd4YTu6aEoXJ083QfXhchGh
```

### 3. Configure Environment Variables

Create a `.env` file under both `/app/` and `/frontend/`.

**`app/.env`**

```env
OPENAI_API_KEY=your-openai-api-key
ORIGINS=http://localhost:8501
```

**`frontend/.env`**

```env
BACKEND_URL=http://localhost:8000
```

---

### 4. Launch the Backend (FastAPI)

```bash
uvicorn app.main:app --reload --port 8000
```

---

### 5. Launch the Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

---

## 💡 Features

- Intent & Entity Extraction with LLM
- Query Rewriting for Semantic Search
- FAISS-based Vector Retrieval
- Context-Aware Answer Generation
- Streamlit Chat Interface

---

## 📦 Docker Support

Coming soon: `Dockerfile` for full containerized deployment.

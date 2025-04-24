# Nutrition Recipe Retrieval System

This project implements a semantic search system for gym-style nutrition recipes using dense embeddings and FAISS.

## Setup

```bash
pip install -r requirements.txt
```

## Build Index (Step 1-4)

```bash
python scripts/build_index.py
```

## Output Files

- `index/combined_index.faiss`: FAISS search index
- `index/combined_metadata.json`: Metadata used in retrieval
- `combined_recipe_dataset.csv`: Merged DB1 and DB2 dataset
- `retrieval_utils.py`: Search function for backend
- `combined_embeddings.npy`: Embedding matrix (optional)

## Example Usage

```python
from retrieval_utils import search

results = search("high protein vegan dinner", top_k=3)
for r in results:
    print(r["recipe_name"], r["tags"])
```

## Deployment

Deliver these files to backend:

- `index/combined_index.faiss`
- `index/combined_metadata.json`
- `scripts/retrieval_utils.py`

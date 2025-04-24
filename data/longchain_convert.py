# Use updated imports to resolve deprecation warnings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import json
import math # Import math to check for NaN

# Function to clean NaN values (common when reading from Pandas DataFrames)
def clean_value(value):
    if isinstance(value, float) and math.isnan(value):
        return None # Convert NaN to None (JSON serializable)
    return value

# --- Configuration ---
METADATA_FILE_PATH = "index/combined_metadata.json" # Path to your metadata JSON
SAVE_PATH = "index/langchain_faiss" # Where to save the LangChain index
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # Make sure this matches your setup
CONTENT_KEY = "preview" # The key containing the main text for embedding

# Step 1: 读取你的原始 metadata
print(f"Loading metadata from {METADATA_FILE_PATH}...")
try:
    with open(METADATA_FILE_PATH) as f:
        metadata_list = json.load(f)
    print(f"Successfully loaded {len(metadata_list)} entries.")
except FileNotFoundError:
    print(f"Error: Metadata file not found at {METADATA_FILE_PATH}")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {METADATA_FILE_PATH}. Check file format.")
    exit(1)


# Step 2: 构造 Document 列表
print("Constructing LangChain Document objects...")
documents = []
skipped_entries = 0
for i, entry in enumerate(metadata_list):
    # Get the main content, use .get() for safety, default to empty string if key missing
    page_content = entry.get(CONTENT_KEY, "")

    if not page_content:
        print(f"Warning: Entry {i} (doc_id: {entry.get('doc_id', 'N/A')}) has empty or missing '{CONTENT_KEY}'. Skipping metadata association or content.")
        # Decide if you want to skip the entry entirely or just embed an empty string
        # If you want to embed an empty string but keep metadata:
        # page_content = ""
        # If you want to skip entirely (as example below):
        # skipped_entries += 1
        # continue # Uncomment this line to skip entries with no content

    # Prepare metadata: include all keys EXCEPT the content key, clean NaN values
    entry_metadata = {}
    for k, v in entry.items():
        if k != CONTENT_KEY:
            entry_metadata[k] = clean_value(v) # Clean potential NaN values

    documents.append(Document(
        page_content=page_content,
        metadata=entry_metadata
    ))

print(f"Constructed {len(documents)} Document objects.")
# if skipped_entries > 0:
#     print(f"Skipped {skipped_entries} entries due to missing/empty content key '{CONTENT_KEY}'.")


# Step 3: 加载原始的嵌入模型
print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
print("Embedding model loaded.")

# Step 4: 构建 FAISS 向量库对象
print("Building FAISS vector store from documents (this may take a while)...")
vectorstore = FAISS.from_documents(documents, embedding)
print("FAISS vector store built.")

# Step 5: 保存成 LangChain 可加载格式
print(f"Saving FAISS index to {SAVE_PATH}...")
vectorstore.save_local(SAVE_PATH)
print(f"Successfully saved LangChain FAISS index to {SAVE_PATH}.")
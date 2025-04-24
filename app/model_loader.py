# app/model_loader.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.prompts import *
from langchain_community.vectorstores import FAISS # Updated import
from langchain_community.embeddings import HuggingFaceEmbeddings # Updated import
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
import logging
import os
import gcsfs
import tempfile
import gdown
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
LANGCHAIN_FAISS_PATH = "data/index/langchain_faiss"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gpt-3.5-turbo" 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _download_faiss_index_from_gcs() -> str:
    fs = gcsfs.GCSFileSystem()
    bucket_path = "nutrirag-index/langchain_faiss"
    tmpdir = tempfile.mkdtemp()
    fs.get(f"{bucket_path}/index.faiss", f"{tmpdir}/index.faiss")
    fs.get(f"{bucket_path}/index.pkl", f"{tmpdir}/index.pkl")
    return tmpdir  # local path to FAISS index files

def _ensure_faiss_index_exists(local_dir=LANGCHAIN_FAISS_PATH):
    index_files = ["index.faiss", "index.pkl"]
    drive_base_url = "https://drive.google.com/uc?id="

    drive_file_ids = {
        "index.faiss": "1eP4fjTfrqoYSh8SFdD0V2ZRfscNjyn1R",
        "index.pkl": "1rMq_T1jsGCnmsgI7ppo_Q1thgCJC7HG_"
    }

    os.makedirs(local_dir, exist_ok=True)

    for fname in index_files:
        local_path = os.path.join(local_dir, fname)
        if not os.path.exists(local_path):
            print(f"📥 Downloading {fname} from Google Drive using gdown...")
            file_id = drive_file_ids[fname]
            # Construct the standard Drive file URL for gdown
            drive_url = f'https://drive.google.com/uc?id={file_id}'
            try:
                gdown.download(drive_url, local_path, quiet=False)
                print(f"✅ Successfully downloaded {fname}")
            except Exception as e:
                print(f"❌ Error downloading {fname}: {e}")
                # Consider removing the potentially incomplete file
                if os.path.exists(local_path):
                    os.remove(local_path)


# --- Initialization Function ---
def initialize_rag_resources():
    """Loads and initializes all RAG components based on the provided snippet."""

    is_cloud_env = os.getenv("IS_CLOUD_ENV", "false").lower() == "true"
    if is_cloud_env:
        index_path = _download_faiss_index_from_gcs()
    else:
        _ensure_faiss_index_exists()
        index_path = LANGCHAIN_FAISS_PATH 

    logging.info("--- Starting RAG Resource Initialization ---")
    embedding = None
    vectorstore = None
    retriever = None
    llm = None
    intent_extraction_chain = None
    rewrite_chain = None
    answer_chain = None 


    # 1. Initialize LLM (You need to replace this with your actual LLM setup)
    logging.info("Initializing LLM (OpenAI GPT)...")
    try:
        # Ensure OPENAI_API_KEY environment variable is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        # Select the GPT model, e.g., "gpt-4o", "gpt-3.5-turbo"
        llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.7)
        logging.info("LLM (OpenAI GPT) initialized.")
    except Exception as e:
        logging.error(f"Error initializing OpenAI LLM: {e}", exc_info=True)
        raise

    # 2. Load Embedding Model
    logging.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        logging.info("Embedding model loaded.")
    except Exception as e:
        logging.error(f"Error loading embedding model: {e}", exc_info=True)
        raise

    # 3. Load FAISS Index
    logging.info(f"Loading LangChain FAISS index from {index_path}...")
    try:
        vectorstore = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
        logging.info("FAISS index loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading FAISS index: {e}", exc_info=True)
        raise

    # 4. Create Retriever
    logging.info("Creating Retriever...")
    try:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        logging.info("Retriever created.")
    except Exception as e:
        logging.error(f"Error creating retriever: {e}", exc_info=True)
        raise

    # 5. Create LLM Chains
    logging.info("Creating LLM chains...")
    try:
        # Step 1: Structure Extraction Chain
        intent_prompt = PromptTemplate(input_variables=["query"], template=query_clean_prompt()) # Assuming query_clean_prompt returns the template string
        intent_extraction_chain = LLMChain(llm=llm, prompt=intent_prompt)
        print(f"intent_extraction_chain: {intent_extraction_chain}")

        # Step 2: Query Rewrite Chain
        rewrite_prompt = PromptTemplate(input_variables=["intent", "entities"], template=generate_reconstruct_prompt()) # Assuming generate_reconstruct_prompt returns the template string
        rewrite_chain = LLMChain(llm=llm, prompt=rewrite_prompt)
        print(f"rewrite_chain: {rewrite_chain}")

        # Step 3: Final Answer Generation Chain
        final_prompt = PromptTemplate(input_variables=["question", "context", "formatted_history"], template=final_generation_prompt_template())
        answer_chain = LLMChain(llm=llm, prompt=final_prompt)
        print(f"answer_chain: {answer_chain}")

        logging.info("LLM Chains created.")
    except Exception as e:
        logging.error(f"Error creating LLM chains: {e}", exc_info=True)
        raise

    logging.info("--- RAG Resource Initialization Complete ---")

    return {
        "embedding": embedding,
        "vectorstore": vectorstore,
        "retriever": retriever,
        "llm": llm,
        "intent_extraction_chain": intent_extraction_chain,
        "rewrite_chain": rewrite_chain,
        "answer_chain": answer_chain
    }

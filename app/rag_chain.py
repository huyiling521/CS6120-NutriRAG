# app/rag_chain.py

from langchain.prompts import PromptTemplate
from app.prompts import *
from langchain.docstore.document import Document
from app.model_loader import *
from fastapi import Request
import re
import json
import logging


def _preprocess_user_query(user_query: str, request: Request) -> dict:
    """Preprocesses the user query using intent extraction and rewriting chains."""
    # Extract intent and entities
    intent_result = request.app.state.rag_resources["intent_extraction_chain"].invoke({"query": user_query})

    raw_json_str = intent_result["text"]
    logging.info(f"Raw JSON String from intent extraction: {raw_json_str}")

    try:
        parsed = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON from intent extraction: {e}")
        # Handle error: maybe return a default structure or raise an exception
        # For now, let's return a structure indicating failure
        return {
            "cleaned_query": user_query, # Or None
            "intent": "unknown",
            "entities": {},
            "semantic_query": user_query # Fallback to original query
        }

    # Rewrite the query based on intent and entities for semantic search
    optimized_query_result = request.app.state.rag_resources["rewrite_chain"].invoke(
        {
            "intent": parsed["intent"],
            "entities": parsed["entities"]
        }
    )

    optimized_query = optimized_query_result["text"]
    # Clean up the rewritten query (remove fluff, normalize whitespace)
    processed_query = _query_preprocess(optimized_query)
    logging.info(f"Processed Semantic Query: {processed_query}")
    return {
        "cleaned_query": parsed["cleaned_query"],
        "intent": parsed["intent"],
        "entities": parsed["entities"],
        "semantic_query": processed_query
    }


def _retrieve_docs(semantic_query: str, request: Request) -> list[Document]:
    """Retrieves relevant documents based on the semantic query."""
    logging.info(f"Retrieving documents for semantic query: {semantic_query}")
    try:
        # Use the retriever loaded during application startup
        retrieved_docs = request.app.state.rag_resources["retriever"].invoke(semantic_query) # Use invoke() for newer LangChain versions
        logging.info(f"Retrieved {len(retrieved_docs)} documents.")
        return retrieved_docs
    except Exception as e:
        logging.error(f"Error during document retrieval: {e}", exc_info=True)
        return [] # Return empty list on error


def _process_retrieved_docs(retrieved_docs: list[Document]) -> str:
    """Formats the retrieved documents into a single string context for the LLM."""
    context_parts = []
    logging.debug("--- Processing Retrieved Documents ---")
    if not retrieved_docs:
        logging.warning("No relevant documents found by retriever.")
        # Provide a neutral context if no documents are found
        context_string = "No specific recipe information found based on the query."
    else:
        for i, doc in enumerate(retrieved_docs):
            # Extract relevant information from the document metadata and content
            recipe_name = doc.metadata.get("recipe_name", "Unknown Recipe")
            # Prioritize using a 'preview' field if available, otherwise use page_content
            content_snippet = doc.metadata.get("preview", doc.page_content)
            ingredients_snippet = doc.metadata.get("ingredients", "")

            # Limit snippet length for conciseness
            content_snippet = (content_snippet[:250] + '...') if len(content_snippet) > 250 else content_snippet
            ingredients_str = f"\nMain ingredients: {ingredients_snippet[:100]}..." if ingredients_snippet else ""

            logging.debug(f"Doc {i+1}: Name='{recipe_name}', Snippet Length={len(content_snippet)}")

            # Format information for each document
            context_parts.append(f"Relevant Document {i+1}:\nRecipe Name: {recipe_name}\nContent Snippet: {content_snippet}{ingredients_str}\n---")

        # Combine all parts into a single context string
        context_string = "\n\n".join(context_parts)

    logging.debug(f"Generated Context String (first 500 chars):\n{context_string[:500]}...")

    return context_string


def _query_preprocess(query: str) -> str:
    """Applies common cleaning steps to a query, often after LLM rewriting."""

    processed_query = query.strip()

    # Remove common LLM introductory phrases
    common_fluff = [
        "Optimized Search Query:",
        "Search Query:",
        "Here is the query:",
        "Rewritten query:",
        "healthy"
        ] # Added "healthy" as it often gets prepended unnecessarily
    processed_query_lower = processed_query.lower()
    for fluff in common_fluff:
        fluff_lower = fluff.lower()
        if processed_query_lower.startswith(fluff_lower):
            processed_query = processed_query[len(fluff):].strip()
            processed_query_lower = processed_query.lower() # Update lower version after stripping

    # Remove surrounding quotes
    if (processed_query.startswith('"') and processed_query.endswith('"')) or \
       (processed_query.startswith("'") and processed_query.endswith("'")):
        processed_query = processed_query[1:-1].strip()

    # Normalize whitespace
    processed_query = re.sub(r'\s+', ' ', processed_query).strip()

    return processed_query



async def full_rag_pipeline(user_query: str, request: Request) -> dict:
    """Executes the full RAG pipeline: preprocess, retrieve, generate.

    Args:
        user_query: The user's natural language query.
        request: The FastAPI request object, used to access shared resources.

    Returns:
        A dictionary containing the final answer and potentially intermediate results.
    """

    logging.info(f"--- Starting Full RAG Pipeline for query: '{user_query}' ---")

    # 1. Preprocess Query (Intent Extraction, Rewriting, Cleaning)
    preprocess_result = _preprocess_user_query(user_query, request)
    semantic_query = preprocess_result["semantic_query"]

    if not semantic_query:
        logging.warning("Preprocessing resulted in an empty semantic query. Aborting.")
        return {"error": "Sorry, I could not process your query after preprocessing.", "final_answer": "Sorry, I could not process your query."} # Return error structure

    logging.info(f"Using Semantic Query for Retrieval: {semantic_query}")

    # 2. Retrieve Documents
    retrieved_docs = _retrieve_docs(semantic_query, request)

    # 3. Process Retrieved Documents into Context
    context_string = _process_retrieved_docs(retrieved_docs)

    # 4. Generate Final Answer using LLM with Context
    logging.info(f"Generating final answer using context (length: {len(context_string)} chars)")
    try:
        # Use the final answering chain
        final_chain = request.app.state.rag_resources["answer_chain"]
        llm_response = final_chain.invoke({"question": user_query, "context": context_string})
        markdown_answer = llm_response["text"]

        logging.info("Successfully generated final answer.")

    except Exception as e:
        logging.error(f"Error during final answer generation: {e}", exc_info=True)
        markdown_answer = "Sorry, an error occurred while generating the final response."

    logging.info(f"--- Finished Full RAG Pipeline ---")
    return markdown_answer

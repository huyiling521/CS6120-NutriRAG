# app/rag_chain.py

from langchain.prompts import PromptTemplate
from app.prompts import *
from langchain.docstore.document import Document
from app.model_loader import *
from fastapi import Request
import re
import json
import logging


def _preprocess_user_query(user_query: str, request: Request):
    intent_result = request.app.state.rag_resources["intent_extraction_chain"].invoke({"query": user_query})
    
    raw_json_str = intent_result["text"]
    logging.info(f"Raw JSON String: {raw_json_str}")
    
    parsed = json.loads(raw_json_str)


    optimized_query_result = request.app.state.rag_resources["rewrite_chain"].invoke(
        {
            "intent": parsed["intent"],
            "entities": parsed["entities"]
        }
    )
    
    optimized_query = optimized_query_result["text"]
    processed_query = _query_preprocess(optimized_query)
    logging.info(f"Processed Query: {processed_query}")
    return {
        "cleaned_query": parsed["cleaned_query"],
        "intent": parsed["intent"],
        "entities": parsed["entities"],
        "semantic_query": processed_query
    }


def _retrieve_docs(semantic_query: str, request: Request) -> list[Document]:
    """根据语义查询检索相关文档。"""
    print(f"Retrieving documents for semantic query: {semantic_query}")
    try:
        # Use the retriever created during initialization
        retrieved_docs = request.app.state.rag_resources["retriever"].invoke(semantic_query) # Use invoke() for newer LangChain versions
        print(f"Retrieved {len(retrieved_docs)} documents.")
        return retrieved_docs
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return [] # Return empty list on error


def _process_retrieved_docs(retrieved_docs: list[Document]) -> str:
    context_parts = []
    logging.debug("--- Retrieved Documents ---")
    if not retrieved_docs:
        logging.warning("No relevant documents found by retriever.")
        context_string = "No relevant recipe information found." # 或者空字符串 ""
    else:
        for i, doc in enumerate(retrieved_docs):
            # --- 从 doc 中提取你需要的信息 ---
            recipe_name = doc.metadata.get("recipe_name", "Unknown recipe")
            # 优先用 preview，如果没有则用 page_content (假设 page_content 是 preview 的内容)
            content_snippet = doc.metadata.get("preview", doc.page_content)
            # 可以再加一些其他 metadata 信息，比如 ingredients
            ingredients_snippet = doc.metadata.get("ingredients", "")
            ingredients_str = f"\nmain ingredients: {ingredients_snippet[:100]}..." if ingredients_snippet else ""

            content_snippet = (content_snippet[:200] + '...') if len(content_snippet) > 200 else content_snippet # 限制长度

            logging.debug(f"Doc {i+1}: {recipe_name}")

            # --- 格式化每个文档的信息 ---
            context_parts.append(f"Related recipe {i+1}: {recipe_name}\nContent: {content_snippet}\n---") # ingredients_str)
            # ---------------------------

        # --- 将所有片段合并成一个字符串 ---
        context_string = "\n\n".join(context_parts)
        # ---------------------------------

    logging.debug(f"Context for LLM:\n{context_string[:500]}...")

    return context_string


def _query_preprocess(query: str) -> str:
    """Applies common cleaning steps to an LLM-generated rewritten query."""

    processed_query = query.strip()
    processed_query = processed_query.lower()

    # Remove common LLM fluff
    common_fluff = ["Optimized Search Query:", "Search Query:", "Here is the query:"]
    for fluff in common_fluff:
        if processed_query.lower().startswith(fluff.lower()):
            processed_query = processed_query[len(fluff):].strip()

    # Remove quotes
    if processed_query.startswith('"') and processed_query.endswith('"'):
        processed_query = processed_query[1:-1].strip()
    elif processed_query.startswith("'") and processed_query.endswith("'"):
        processed_query = processed_query[1:-1].strip()

    # clean whitespace
    processed_query = re.sub(r'\s+', ' ', processed_query).strip()
    
    return processed_query



async def full_rag_pipeline(user_query: str, request: Request) -> str:
    """完整的 RAG 流程，接收用户查询并返回 Markdown 格式的推荐。

    Args:
        user_query: 用户的自然语言查询。

    Returns:
        Markdown 格式的推荐结果。
    """

    logging.info(f"--- Starting Full RAG Pipeline for query: '{user_query}' ---")

    # 1. 解析查询
    preprocess_result = _preprocess_user_query(user_query, request)
    semantic_query = preprocess_result["semantic_query"]

    if not semantic_query:
        logging.warning("Preprocessing resulted in an empty semantic query. Aborting.")
        return "抱歉，无法处理您的查询。"
    
    logging.info(f"Semantic Query: {semantic_query}")
    
     # 2. 检索文档
    retrieved_docs = _retrieve_docs(semantic_query, request)

    # 3. 处理检索到的文档，生成上下文
    context_string = _process_retrieved_docs(retrieved_docs)

    logging.info(f"Context String: {context_string}")
    
    # 3. 构建 Prompt (TODO)
    try:
        llm_response = request.app.state.rag_resources["answer_chain"].invoke({"question": user_query, "context": context_string})
        markdown_answer = llm_response["text"]

        logging.info("Successfully generated final answer.")

    except Exception as e:
        logging.error(f"Error during final answer generation: {e}", exc_info=True)
        markdown_answer = "抱歉，在生成最终答案时遇到错误。"

    logging.info(f"--- Finished Full RAG Pipeline ---")
    return markdown_answer

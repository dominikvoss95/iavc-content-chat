import os
import uuid
import datetime
import trafilatura
import httpx
from typing import Dict, Any, List
from src.state import IAVCGraphState, ArticleChunk
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import src.database as db

load_dotenv()

# Global Embedding Model Initialization (Local-only)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def fetch_source_page(state: IAVCGraphState) -> Dict[str, Any]:
    """
    Fetches the raw HTML content of a source page.
    
    Args:
        state (IAVCGraphState): The current graph state containing 'source_url'.
        
    Returns:
        Dict[str, Any]: Updated state with 'raw_payload' and 'fetch_status'.
    """
    url = state.get("source_url")
    if not url:
        return {"fetch_status": "error", "error_message": "No source URL provided."}
    
    try:
        headers = {"User-Agent": "IAVC-Bot/1.0 (Local-Integration)"}
        response = httpx.get(url, headers=headers, timeout=15.0)
        response.raise_for_status()
        
        return {
            "raw_payload": response.text,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "fetch_status": "success"
        }
    except Exception as error:
        return {
            "fetch_status": "error",
            "error_message": f"Error fetching page: {str(error)}"
        }

def extract_article_links(state: IAVCGraphState) -> Dict[str, Any]:
    raw_payload = state.get("raw_payload", "")
    source_url = state.get("source_url", "")
    if not raw_payload:
        return {"article_links": []}

    # If it's a direct HTML link, return it immediately as the single article to process
    if ".html" in source_url or source_url.endswith(".php") or any(c.isdigit() for c in source_url.split("/")[-1]):
        return {"article_links": [source_url]}

    # Simpler fallback for category pages: find all links starting with the domain
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw_payload, "html.parser")
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/'):
            from urllib.parse import urljoin
            href = urljoin(source_url, href)
        if source_url in href and len(href) > len(source_url) + 5:
            links.append(href)
    
    return {"article_links": list(set(links))[:5]}

def fetch_article(state: IAVCGraphState) -> Dict[str, Any]:
    """
    Fetches the full article content from the first discovered link or direct source URL.
    
    Args:
        state (IAVCGraphState): The current graph state.
        
    Returns:
        Dict[str, Any]: State with 'article_content' and 'article_url'.
    """
    links = state.get("article_links", [])
    url = links[0] if links else state.get("source_url")
    
    try:
        headers = {"User-Agent": "IAVC-Bot/1.0"}
        response = httpx.get(url, headers=headers, timeout=15.0)
        response.raise_for_status()
        
        return {
            "article_url": url,
            "article_content": response.text,
            "fetch_status": "success"
        }
    except Exception as error:
        return {
            "fetch_status": "error", 
            "error_message": f"Error fetching article: {str(error)}"
        }

def parse_article(state: IAVCGraphState) -> Dict[str, Any]:
    """
    Extracts clean text and metadata (title, author, date) from HTML content.
    
    Args:
        state (IAVCGraphState): Current state with 'article_content'.
        
    Returns:
        Dict[str, Any]: State with extracted metadata and parsed content.
    """
    content = state.get("article_content", "")
    if not content:
        return {"parse_status": "error", "error_message": "No content available for parsing."}
    
    result = trafilatura.extract(content, include_comments=False, include_tables=True)
    metadata = trafilatura.metadata.extract_metadata(content)
    
    if not result:
        return {"parse_status": "error", "error_message": "Failed to extract text content."}

    return {
        "article_title": getattr(metadata, 'title', 'Unknown Title'),
        "article_category": state.get("category_name", "General"),
        "published_at": getattr(metadata, 'date', datetime.datetime.now(datetime.timezone.utc).isoformat()),
        "firma": getattr(metadata, 'author', 'IAVC World Editorial'),
        "article_content": result,
        "parse_status": "success"
    }

def validate_article(state: IAVCGraphState) -> Dict[str, Any]:
    content = state.get("article_content", "")
    if not content or len(content.strip()) < 200:
        return {"validation_status": "failed", "error_message": "Content too short"}
    return {"validation_status": "success"}

def chunk_article(state: IAVCGraphState) -> Dict[str, Any]:
    content = state.get("article_content", "")
    if not content:
        return {"chunks": []}
    
    chunk_size = 800
    overlap = 150
    chunks = []
    
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        if end < len(content):
            last_space = content.rfind(' ', start, end)
            if last_space > start + chunk_size // 2:
                end = last_space
        
        text_chunk = content[start:end].strip()
        if len(text_chunk) > 50:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "article_url": state.get("article_url", ""),
                "article_title": state.get("article_title", ""),
                "article_category": state.get("article_category", ""),
                "published_at": state.get("published_at", ""),
                "firma": state.get("firma", "Unbekannt"),
                "text": text_chunk
            })
        start = end - overlap if end < len(content) else len(content)
        if start >= len(content): break
        
    return {"chunks": chunks}

def embed_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    """
    Generates semantic vector embeddings for the extracted chunks using HuggingFace.
    
    Args:
        state (IAVCGraphState): Current state with 'chunks'.
        
    Returns:
        Dict[str, Any]: State with updated 'chunks' containing 'raw_vector'.
    """
    chunks = state.get("chunks", [])
    if not chunks:
        return {"embedding_status": "skipped"}
        
    texts = [c["text"] for c in chunks]
    try:
        vector_embeddings = embeddings.embed_documents(texts)
        for i, chunk in enumerate(chunks):
            chunk["embedding_id"] = f"vec_{i}" 
            chunk["raw_vector"] = vector_embeddings[i]
            
        return {"chunks": chunks, "embedding_status": "success"}
    except Exception as error:
        return {"embedding_status": "error", "error_message": f"Embedding failed: {str(error)}"}

def index_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    """
    Permanently stores chunks and embeddings in the local SQLite-vec database.
    
    Args:
        state (IAVCGraphState): State with embedded 'chunks'.
        
    Returns:
        Dict[str, Any]: Indexing status.
    """
    chunks = state.get("chunks", [])
    try:
        for c in chunks:
            db.insert_chunk(
                chunk_id=c["chunk_id"],
                url=c.get("article_url", ""),
                title=c.get("article_title", ""),
                category=c.get("article_category", ""),
                date=c.get("published_at", ""),
                firma=c.get("firma", ""),
                text=c["text"],
                embedding=c["raw_vector"]
            )
        return {"index_status": "success"}
    except Exception as error:
        return {"index_status": "error", "error_message": f"DB entry failed: {str(error)}"}

# --- Query Nodes ---

def generate_answer(state: IAVCGraphState) -> Dict[str, Any]:
    query = state.get("user_query", "")
    chunks = state.get("retrieved_chunks", []) # Usually would come from DB
    
    # Context building (using the chunks we just processed if retrieval is empty)
    # This is helpful for testing 'ingest then immediate answer'
    source_material = chunks if chunks else state.get("chunks", [])
    
    # Format instructions with Metadata
    context = ""
    for c in source_material[:3]:
        context += f"Titel: {c.get('article_title', 'Unbekannt')}\n"
        context += f"Datum: {c.get('published_at', 'Unbekannt')}\n"
        context += f"Firma/Autor: {c.get('firma', 'Unbekannt')}\n"
        context += f"Inhalt: {c.get('text', '')}\n\n"
    
    # Talk to local Ollama
    try:
        llm = ChatOllama(model="phi3", temperature=0) # ensure you have llama3 pulled
        
        prompt = ChatPromptTemplate.from_template("""
        Du bist ein hilfreicher Assistent für die Website IAVC World. 
        Beantworte die Frage NUR basierend auf dem folgenden Kontext.
        Wenn die Antwort nicht im Kontext steht, sag dass du es nicht weißt.
        
        Kontext:
        {context}
        
        Frage: {query}
        """)
        
        chain = prompt | llm
        response = chain.invoke({"context": context, "query": query})
        
        return {
            "answer_text": response.content,
            "generation_status": "success"
        }
    except Exception as e:
        return {
            "answer_text": f"Fehler bei Ollama: {str(e)}. Stelle sicher, dass 'ollama serve' läuft und 'llama3' installiert ist.",
            "generation_status": "error"
        }

def receive_query(state: IAVCGraphState) -> Dict[str, Any]:
    return {"retrieval_status": "pending"}

def retrieve_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    query = state.get("user_query", "")
    try:
        query_vec = embeddings.embed_query(query)
        results = db.search_similar_chunks(query_vec, top_k=5)
        return {"retrieved_chunks": results, "retrieval_status": "success"}
    except Exception as e:
        print("Retrieval Error:", str(e))
        return {"retrieval_status": "error"}

def optionally_rerank_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    return {"retrieval_status": "done"}

def format_sources(state: IAVCGraphState) -> Dict[str, Any]:
    chunks = state.get("retrieved_chunks", [])
    sources = []
    # Deduplicate sources based on URL so we don't return the same article 3 times
    seen_urls = set()
    for c in chunks:
        url = c.get("article_url")
        if url not in seen_urls:
            sources.append({
                "title": c.get("article_title"),
                "url": url,
                "published_at": c.get("published_at"),
                "firma": c.get("firma")
            })
            seen_urls.add(url)
    return {"answer_sources": sources}

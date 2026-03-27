import uuid
import datetime
from typing import Dict, Any
from bs4 import BeautifulSoup
import httpx
from src.state import IAVCGraphState, ArticleChunk

def fetch_source_page(state: IAVCGraphState) -> Dict[str, Any]:
    url = state.get("source_url")
    if not url:
        return {"fetch_status": "error", "error_message": "No source_url provided"}
    
    try:
        # For MVP we can just mock the response or do a real fetch. 
        # We will do a real fetch but catch errors gracefully for testability.
        # Adding a fake user-agent:
        headers = {"User-Agent": "IAVC-Bot/1.0"}
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        
        return {
            "raw_payload": response.text,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "fetch_status": "success"
        }
    except Exception as e:
        return {
            "fetch_status": "error",
            "error_message": str(e)
        }

def extract_article_links(state: IAVCGraphState) -> Dict[str, Any]:
    raw_payload = state.get("raw_payload", "")
    if not raw_payload:
        return {"article_links": []}

    soup = BeautifulSoup(raw_payload, "html.parser")
    links = []
    # Mocking extraction logic targeting potential article links
    for a in soup.find_all('a', href=True):
        href = a['href']
        # simple heuristic for articles
        if href.startswith('http') and len(href) > 20: 
            links.append(href)
    
    return {"article_links": list(set(links))[:5]} # returning top 5 links for simplicity

def fetch_article(state: IAVCGraphState) -> Dict[str, Any]:
    # We will fetch the first article link if any for the test pipeline
    links = state.get("article_links", [])
    if not links:
        return {"fetch_status": "error", "error_message": "No article_links to fetch"}
    
    url = links[0]
    
    try:
        headers = {"User-Agent": "IAVC-Bot/1.0"}
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        
        return {
            "article_url": url,
            "article_content": response.text,
            "fetch_status": "success"
        }
    except Exception as e:
        return {
            "fetch_status": "error",
            "error_message": str(e)
        }

def parse_article(state: IAVCGraphState) -> Dict[str, Any]:
    content = state.get("article_content", "")
    if not content:
        return {"parse_status": "error", "error_message": "No article_content to parse"}
    
    soup = BeautifulSoup(content, "html.parser")
    title = soup.find('title').text if soup.find('title') else "Unknown Title"
    
    # Extract main text
    paragraphs = soup.find_all('p')
    text = "\n".join([p.text for p in paragraphs])
    
    category = state.get("category_name", "General")
    published_at = datetime.datetime.now(datetime.timezone.utc).isoformat() # Mock date
    
    return {
        "article_title": title,
        "article_category": category,
        "published_at": published_at,
        "article_content": text,
        "parse_status": "success"
    }

def validate_article(state: IAVCGraphState) -> Dict[str, Any]:
    content = state.get("article_content", "")
    title = state.get("article_title", "")
    
    if len(content.strip()) < 50:
        return {"validation_status": "failed", "error_message": "Article content too short"}
    if not title:
        return {"validation_status": "failed", "error_message": "No title found"}
        
    return {"validation_status": "success"}

def chunk_article(state: IAVCGraphState) -> Dict[str, Any]:
    content = state.get("article_content", "")
    if not content:
        return {"chunks": []}
    
    # Simple character-based chunking
    chunk_size = 500
    overlap = 50
    chunks = []
    
    # Very basic chunking logic
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        text_chunk = content[start:end]
        
        chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "article_url": state.get("article_url", ""),
            "article_title": state.get("article_title", ""),
            "article_category": state.get("article_category", ""),
            "published_at": state.get("published_at", ""),
            "text": text_chunk
        })
        start += (chunk_size - overlap)
        
    return {"chunks": chunks}

def embed_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    chunks = state.get("chunks", [])
    # For MVP: mock embeddings by using length or hashing, but since we mock, let's just add an embedding_id
    for chunk in chunks:
        chunk["embedding_id"] = f"emb_{uuid.uuid4()}"
    return {"chunks": chunks, "embedding_status": "success"}

def index_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    # Mock indexing logic into an MVP SQLite DB or just in-memory
    # For now, we will just return success 
    return {"index_status": "success"}

# --- Query Graph Nodes ---

def receive_query(state: IAVCGraphState) -> Dict[str, Any]:
    query = state.get("user_query")
    if not query:
        return {"error_message": "Empty query"}
    return {"retrieval_status": "pending"}

def retrieve_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    query = state.get("user_query")
    # Mock retrieval logic
    mock_retrieved = [{
        "chunk_id": "mock_1",
        "article_url": "https://example.com",
        "article_title": "Mock Article",
        "article_category": "News",
        "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "text": f"This is a mock chunk containing info about {query}.",
        "score": 0.95
    }]
    return {"retrieved_chunks": mock_retrieved, "retrieval_status": "success"}

def optionally_rerank_chunks(state: IAVCGraphState) -> Dict[str, Any]:
    chunks = state.get("retrieved_chunks", [])
    return {"retrieved_chunks": chunks} # Pass through for now

def generate_answer(state: IAVCGraphState) -> Dict[str, Any]:
    chunks = state.get("retrieved_chunks", [])
    if not chunks:
        return {"answer_text": "I could not find any relevant information to answer your question.", "generation_status": "failed"}
    
    context = "\n".join([c.get("text", "") for c in chunks])
    answer = f"Based on the sources, here is what I found:\n{context}"
    return {"answer_text": answer, "generation_status": "success"}

def format_sources(state: IAVCGraphState) -> Dict[str, Any]:
    chunks = state.get("retrieved_chunks", [])
    sources = []
    for c in chunks:
        sources.append({
            "title": c.get("article_title"),
            "url": c.get("article_url"),
            "published_at": c.get("published_at")
        })
    return {"answer_sources": sources}

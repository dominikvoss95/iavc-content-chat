import os
import time
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.graph import build_ingestion_graph, build_query_graph

app = FastAPI(title="IAVC World Content Chat Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In Produktion hier "https://iavcworld.de" eintragen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ingestion_graph = build_ingestion_graph()
query_graph = build_query_graph()

# --- Security & Rate Limiting ---
API_KEY = os.environ.get("IAVC_API_KEY", "your-secret-api-key-here") # Change this in production!
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

# Simple in-memory rate limiting (10 requests per minute per IP)
# In production, use Redis or a proper library like slowapi
rate_limits = {}

def check_rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    
    if ip not in rate_limits:
        rate_limits[ip] = []
        
    # Clean up old limits (older than 60 seconds)
    rate_limits[ip] = [t for t in rate_limits[ip] if now - t < 60]
    
    if len(rate_limits[ip]) >= 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
    rate_limits[ip].append(now)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials - Invalid API Key."
        )
# --------------------------------

class IngestRequest(BaseModel):
    source_url: str
    category_name: str = "General"
    debug: bool = False

class QueryRequest(BaseModel):
    user_query: str
    top_k: int = 5
    category_filter: str = ""
    date_filter: str = ""
    debug: bool = False

@app.post("/ingest", dependencies=[Security(verify_api_key)])
async def ingest_content(request: IngestRequest, req: Request):
    check_rate_limit(req)
    run_id = str(uuid.uuid4())
    initial_state = {
        "source_identifier": str(uuid.uuid4()),
        "source_url": request.source_url,
        "category_name": request.category_name,
        "run_id": run_id,
        "current_time": datetime.now(timezone.utc).isoformat(),
        "debug": request.debug
    }
    
    try:
        final_state = ingestion_graph.invoke(initial_state)
        return {
            "status": "success", 
            "run_id": run_id, 
            "indexed_chunks": len(final_state.get("chunks", [])),
            "errors": final_state.get("error_message")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", dependencies=[Security(verify_api_key)])
async def query_content(request: QueryRequest, req: Request):
    check_rate_limit(req)
    run_id = str(uuid.uuid4())
    initial_state = {
        "user_query": request.user_query,
        "top_k": request.top_k,
        "category_filter": request.category_filter,
        "date_filter": request.date_filter,
        "run_id": run_id,
        "debug": request.debug
    }
    
    try:
        final_state = query_graph.invoke(initial_state)
        return {
            "answer": final_state.get("answer_text"),
            "sources": final_state.get("answer_sources", []),
            "retrieval_status": final_state.get("retrieval_status"),
            "generation_status": final_state.get("generation_status")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os
if not os.path.exists("public"):
    os.makedirs("public")
app.mount("/public", StaticFiles(directory="public"), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

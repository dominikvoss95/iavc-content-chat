import sqlite3
import sqlite_vec
import struct
from typing import List, Dict, Any

DB_PATH = "iavc_knowledge.db"

def get_db():
    """
    Returns a database connection with sqlite_vec extension loaded.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the SQLite tables for metadata and vector search.
    """
    conn = get_db()
    
    # We create a virtual table for vector search
    # Vector length depends on the model. all-MiniLM-L6-v2 outputs 384 dimensions.
    conn.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(
            embedding float[384]
        )
    ''')
    
    # And a separate table for the metadata
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chunk_meta(
            rowid INTEGER PRIMARY KEY,
            chunk_id TEXT UNIQUE,
            article_url TEXT,
            article_title TEXT,
            article_category TEXT,
            published_at TEXT,
            firma TEXT,
            text TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def serialize_vector(vector: List[float]) -> bytes:
    """Serialize a list of floats into bytes suitable for sqlite_vec."""
    return struct.pack(f"{len(vector)}f", *vector)

def insert_chunk(chunk_id: str, url: str, title: str, category: str, date: str, firma: str, text: str, embedding: List[float]):
    """
    Inserts a chunk's metadata and its embedding into the database.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Insert metadata first
    cursor.execute('''
        INSERT INTO chunk_meta (chunk_id, article_url, article_title, article_category, published_at, firma, text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (chunk_id, url, title, category, date, firma, text))
    
    rowid = cursor.lastrowid
    
    # Insert embedding into the virtual table at the same rowid
    embedding_bytes = serialize_vector(embedding)
    cursor.execute('''
        INSERT INTO vec_chunks (rowid, embedding)
        VALUES (?, ?)
    ''', (rowid, embedding_bytes))
    
    conn.commit()
    conn.close()

def search_similar_chunks(query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a vector search to find the most similar chunks.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    query_bytes = serialize_vector(query_embedding)
    
    # Perform vector search using sqlite-vec
    cursor.execute('''
        SELECT rowid, distance 
        FROM vec_chunks 
        WHERE embedding MATCH ? 
        ORDER BY distance 
        LIMIT ?
    ''', (query_bytes, top_k))
    
    results = []
    rows = cursor.fetchall()
    
    for r in rows:
        rowid = r[0]
        distance = r[1]
        
        # Fetch metadata
        cursor.execute('SELECT * FROM chunk_meta WHERE rowid = ?', (rowid,))
        meta = cursor.fetchone()
        
        if meta:
            results.append({
                "chunk_id": meta["chunk_id"],
                "article_url": meta["article_url"],
                "article_title": meta["article_title"],
                "article_category": meta["article_category"],
                "published_at": meta["published_at"],
                "firma": meta["firma"],
                "text": meta["text"],
                "distance": distance
            })
            
    conn.close()
    return results

# Automatically init DB on import
init_db()

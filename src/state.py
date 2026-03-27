from typing import List, TypedDict

class ArticleChunk(TypedDict, total=False):
    chunk_id: str
    article_url: str
    article_title: str
    article_category: str
    published_at: str
    text: str
    embedding_id: str
    score: float

class IAVCGraphState(TypedDict, total=False):
    # Ingestion Graph Input
    source_identifier: str
    source_url: str
    category_name: str
    run_id: str
    current_time: str
    debug: bool

    # Ingestion State
    raw_payload: str
    fetched_at: str
    fetch_status: str

    article_links: List[str]

    article_url: str
    article_title: str
    article_category: str
    published_at: str
    article_content: str
    parse_status: str
    validation_status: str

    chunks: List[ArticleChunk]
    embedding_status: str
    index_status: str

    # Query Graph Input
    user_query: str
    top_k: int
    category_filter: str
    date_filter: str

    # Query State
    retrieved_chunks: List[ArticleChunk]
    retrieval_status: str

    answer_text: str
    answer_sources: List[dict]
    generation_status: str

    error_message: str

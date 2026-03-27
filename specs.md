# specs.md

## Specs
IAVC World Content Chat Agent using Python and LangGraph

## Tech Stack
- Python
- LangGraph
- httpx
- BeautifulSoup4 or Trafilatura
- Pydantic or TypedDict for state
- FastAPI
- PostgreSQL + pgvector or Qdrant
- Pytest
- Optional: SQLite for local metadata persistence in MVP
- Optional: OpenAI API or local embedding/chat models

---

## 1. Overview

A Python-based content chat agent that crawls and parses articles from IAVC World, transforms them into searchable chunks, indexes them in a retrieval system, and answers user questions grounded in those website contents.

Stage 1 is implemented as a deterministic LangGraph workflow with fixed nodes and explicit state transitions for ingestion and retrieval.

Stage 2 may extend this into a more agentic system with source prioritization, re-ranking, fallback retrieval, content deduplication, and answer quality evaluation.

---

## 2. Functional Specifications

### 2.1 User Stories

- As a user, I want to ask questions about the content published on IAVC World.
- As a user, I want answers that are grounded in actual articles and include sources.
- As a user, I do not want hallucinated answers when no relevant content is available.
- As a developer, I want the workflow to be modeled as a LangGraph graph so I can learn state, nodes, edges, checkpoints, and tracing.
- As a developer, I want each node to have one clear responsibility and be testable in isolation.

### 2.2 Features

| Feature                  | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| Fetch Source Pages       | Load category pages and article pages from IAVC World                    |
| Parse Article Content    | Extract title, URL, category, publication date, teaser, and main content |
| Validate Content         | Ensure parsed content is usable and not empty or malformed               |
| Chunk Content            | Split article content into retrieval-ready chunks                        |
| Generate Embeddings      | Transform chunks into vector embeddings                                  |
| Index Content            | Store chunk metadata and embeddings in a searchable store                |
| Retrieve Relevant Chunks | Find the most relevant content for a user query                          |
| Generate Grounded Answer | Produce an answer using retrieved chunks only                            |
| Source Attribution       | Return titles, URLs, and publication dates for supporting sources        |
| State Tracking           | Store node outputs and decision flags in graph state                     |
| Error Handling           | Prevent invalid content from being indexed or used for answering         |
| Tracing                  | Make graph execution and retrieval decisions inspectable                 |

---

## 3. Non-Functional Requirements

| Requirement      | Description                                                                         |
| ---------------- | ----------------------------------------------------------------------------------- |
| Reliability      | No fabricated answer when retrieval returns no relevant sources                     |
| Determinism      | Stage 1 must behave deterministically in crawling, parsing, chunking, and indexing  |
| Testability      | Every node must be unit-testable                                                    |
| Observability    | Each node writes status, timestamps, and errors into state                          |
| Maintainability  | Node logic must stay small and separated by responsibility                          |
| Extensibility    | Architecture must support later extension to agentic retrieval and multiple sources |
| Source Grounding | Every answer must be traceable to indexed source chunks                             |
| Reusability      | Ingestion and query workflows should be separable                                   |

---

## 4. Interfaces

### 4.1 Graph Interface

#### Ingestion Graph
- fetch_source_page
- extract_article_links
- fetch_article
- parse_article
- validate_article
- chunk_article
- embed_chunks
- index_chunks

#### Query Graph
- receive_query
- retrieve_chunks
- optionally_rerank_chunks
- generate_answer
- format_sources

---

### 4.2 Input State

#### Ingestion Graph Input
- source_identifier
- source_url
- category_name
- run_id
- current_time
- debug

#### Query Graph Input
- user_query
- top_k
- category_filter
- date_filter
- run_id
- debug

---

### 4.3 Output State

#### Ingestion Graph Output
- raw_payload
- fetched_at
- fetch_status
- article_links
- article_url
- article_title
- article_category
- published_at
- article_content
- parse_status
- validation_status
- chunks
- embedding_status
- index_status
- error_message

#### Query Graph Output
- user_query
- retrieved_chunks
- retrieval_status
- answer_text
- answer_sources
- generation_status
- error_message

---

## 5. Data Model Overview

### 5.1 Graph State

```python
from typing import List, Optional
from typing_extensions import TypedDict

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
    source_identifier: str
    source_url: str
    category_name: str

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

    user_query: str
    top_k: int
    category_filter: str
    date_filter: str

    retrieved_chunks: List[ArticleChunk]
    retrieval_status: str

    answer_text: str
    answer_sources: List[dict]
    generation_status: str

    error_message: str
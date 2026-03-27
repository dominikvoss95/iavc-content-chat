from langgraph.graph import StateGraph, END
from src.state import IAVCGraphState
from src.nodes import (
    fetch_source_page, extract_article_links, fetch_article,
    parse_article, validate_article, chunk_article,
    embed_chunks, index_chunks,
    receive_query, retrieve_chunks, optionally_rerank_chunks,
    generate_answer, format_sources
)

def build_ingestion_graph():
    builder = StateGraph(IAVCGraphState)
    builder.add_node("fetch_source_page", fetch_source_page)
    builder.add_node("extract_article_links", extract_article_links)
    builder.add_node("fetch_article", fetch_article)
    builder.add_node("parse_article", parse_article)
    builder.add_node("validate_article", validate_article)
    builder.add_node("chunk_article", chunk_article)
    builder.add_node("embed_chunks", embed_chunks)
    builder.add_node("index_chunks", index_chunks)

    builder.set_entry_point("fetch_source_page")
    
    # Example edges: 
    builder.add_edge("fetch_source_page", "extract_article_links")
    builder.add_edge("extract_article_links", "fetch_article")
    builder.add_edge("fetch_article", "parse_article")
    builder.add_edge("parse_article", "validate_article")
    
    # Conditional logic based on validation_status
    def validation_router(state: IAVCGraphState):
        if state.get("validation_status") == "failed":
            return END
        else:
            return "chunk_article"
            
    builder.add_conditional_edges(
        "validate_article",
        validation_router,
        {
            END: END,
            "chunk_article": "chunk_article"
        }
    )
    
    builder.add_edge("chunk_article", "embed_chunks")
    builder.add_edge("embed_chunks", "index_chunks")
    builder.add_edge("index_chunks", END)
    
    return builder.compile()

def build_query_graph():
    builder = StateGraph(IAVCGraphState)
    builder.add_node("receive_query", receive_query)
    builder.add_node("retrieve_chunks", retrieve_chunks)
    builder.add_node("optionally_rerank_chunks", optionally_rerank_chunks)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("format_sources", format_sources)

    builder.set_entry_point("receive_query")
    builder.add_edge("receive_query", "retrieve_chunks")
    builder.add_edge("retrieve_chunks", "optionally_rerank_chunks")
    builder.add_edge("optionally_rerank_chunks", "generate_answer")
    builder.add_edge("generate_answer", "format_sources")
    builder.add_edge("format_sources", END)
    
    return builder.compile()

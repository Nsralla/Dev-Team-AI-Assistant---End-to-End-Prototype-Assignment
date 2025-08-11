# root: app/services/router.py
from __future__ import annotations
import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.groq_client import ask_llama3
from app.services.classifier import QueryClassification
from app.services.classifier import classify_query_with_llm
from app.services.sql_gen import llm_generate_sql, execute_sql, llm_compose_answer
from app.services.kb_router import answer_with_kb
from app.services.kb_retriever import search_kb

def route_query(question: str, db: Session) -> Dict[str, Any]:
    cls = classify_query_with_llm(question)

    # DB route
    if cls["route"] == "db":
        domain = cls["domain"]
        sql = llm_generate_sql(question)
        cols, rows = execute_sql(db, sql)
        answer = llm_compose_answer(question, rows)
        return {
            "path": "db", 
            "domain": domain,
            "confidence": cls["confidence"],
            "answer": answer,
            "data": rows,
            "columns": cols
        }

    # KB route
    if cls["route"] == "kb":
        kb_result = answer_with_kb(question)
        return {
            "path": "kb",
            "domain": None,
            "confidence": cls["confidence"],
            "answer": kb_result["answer"],
            "sources": kb_result["sources"]
        }
        
    # Hybrid route: do both, then ask LLM to pick/merge
    if cls["route"] == "hybrid":
        # Implement hybrid approach
        # For now, fall back to KB
        return route_query(question, db) 

    # Safety fallback
    kb_result = answer_with_kb(question)
    return {
        "path": "kb", 
        "domain": None,
        "confidence": 0.4,
        "answer": kb_result["answer"],
        "sources": kb_result["sources"]
    }

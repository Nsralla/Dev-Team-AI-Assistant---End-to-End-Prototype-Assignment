# root: app/services/kb_router.py
from __future__ import annotations
from fastapi import Query
from app.services.kb_retriever import search_kb
from app.services.groq_client import ask_llama3


def answer_with_kb(q:str=Query(...), k:int=5):
    chunks = search_kb(q, k)
    context_text = "\n".join([chunk["text"] for chunk in chunks])
    
    system_prompt = "You are a helpful assistant that answers questions using the provided context."
    user_prompt = f"Answer the following question using ONLY the provided context:\n\nContext:\n{context_text}\n\nQuestion: {q}"
    response = ask_llama3(system_prompt, user_prompt)
    return {
        "question":q,
        "answer": response,
        "sources": chunks
    }



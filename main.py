from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
import logging
import traceback

from app.services.groq_client import ask_llama3
from app.services.kb_retriever import search_kb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Harri Assistant API",
    description="API for loading and serving data from JSON files",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred", "details": str(exc)}
    )

# Request validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {str(exc)}")
    return await request_validation_exception_handler(request, exc)

@app.get('/kb/search')
def kb_search(q:str=Query(...), k:int=5):
    results = search_kb(q, k)
    return results

@app.get('/kb/ask')
def kb_ask(q:str=Query(...), k:int=5):
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

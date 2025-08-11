from __future__ import annotations
from typing import Any, Dict, List, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.services.groq_client import ask_llama3
import re

# Add this logger at the top of the file
logger = logging.getLogger(__name__)

SCHEMAS = {
    "employees": """
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        role TEXT,
        team TEXT,
        jira_username TEXT
    );
    """,
    "jira_tickets": """
    CREATE TABLE jira_tickets (
        id TEXT PRIMARY KEY,
        summary TEXT,
        assignee TEXT,
        status TEXT,
        priority TEXT
    );
    """,
    "deployments": """
    CREATE TABLE deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        version TEXT,
        date TEXT,   -- ISO 8601 string
        status TEXT
    );
    """
}

SQL_SYSTEM = """
You are SQL-Gen — an expert in writing **pure, valid SQLite** queries.

Rules:
1. Use only the provided schema for the selected target table.
2. Output **only** the SQL query (no explanations, comments, or extra text).
3. Always ensure queries are safe:
   - Apply WHERE filters when possible to limit dataset size.
   - Include LIMIT 50 unless the query explicitly specifies a different limit.
4. Use correct SQLite syntax and column names exactly as given in the schema.
5. Never reference tables, columns, or functions not defined in the schema.
6. If a query is ambiguous about filters, return the most reasonable interpretation.
7. For deployments table, use 'date' column for timestamp ordering (NOT 'deployed_at').

Example:
User: "Show all high-priority Jira tickets"
Output:
SELECT * FROM jira_tickets
WHERE priority = 'High'
LIMIT 50;

User: "Show recent deployments"
Output:
SELECT * FROM deployments
ORDER BY date DESC
LIMIT 50;
"""

ANSWER_SYSTEM = """
You are Answer-Gen — an assistant that turns SQL query results into clear, concise answers for the user.

Rules:
1. Input: A natural-language user question and SQL result rows (provided as JSON-like records).
2. Output: A short, direct answer in plain language.
3. If the result set is empty:
   → Respond clearly that no matching records were found.
4. If helpful for clarity:
   → Present results as a compact bullet-point or table-like list (no full SQL tables).
5. Do NOT:
   - Show SQL code
   - Mention SQL execution or database details
6. Keep formatting clean and user-friendly.
"""

def llm_generate_sql(question:str):
    user_prompt = f"""
    User: {question}
    Output:
    "<SQL_QUERY>"
    """
    raw_sql = ask_llama3(SQL_SYSTEM, user_prompt)
    
    # Clean up common SQL syntax issues
    # Add space between LIMIT and number if missing
    raw_sql = re.sub(r'LIMIT(\d+)', r'LIMIT \1', raw_sql)
    # Add other regex fixes as needed
    
    logger.info(f"Generated SQL: {raw_sql}")
    return raw_sql

def execute_sql(db:Session, sql:str):
    try:
        # Add regex to fix common SQL syntax issues
        sql = re.sub(r'LIMIT(\d+)', r'LIMIT \1', sql)
        
        result = db.execute(text(sql))
        cols = list(result.keys())  # Convert to list for serialization
        rows = [dict(zip(cols, r)) for r in result.fetchall()]
        return cols, rows
    except SQLAlchemyError as e:
        logger.error(f"Database error executing SQL: {str(e)}")
        logger.error(f"Problem SQL: {sql}")
        # Return empty results rather than crashing
        return [], []
    except Exception as e:
        logger.error(f"Unexpected error executing SQL: {str(e)}")
        logger.error(f"Problem SQL: {sql}")
        return [], []

def llm_compose_answer(question:str, rows: List[Dict[str, Any]])-> str:
    user_prompt = f"""
        USER: {question}
        CONTEXT: {rows}
    """
    return ask_llama3(ANSWER_SYSTEM, user_prompt)
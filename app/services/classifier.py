from __future__ import annotations
import json
import os
from typing import Literal, TypedDict, Optional
import requests
Route = Literal["db", "kb", "hybrid"]
Domain = Optional[Literal["employees", "deployments", "jira_tickets"]]

class QueryClassification(TypedDict):
    route: Route
    domain:Domain
    confidence:float
    
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "llama-4-scout-17b-16e-instruct") # load the LLM model
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


SYSTEM_PROMPT = """
You are a classification engine.
YOUR OUTPUT MUST BE VALID JSON WITH NO ADDITIONAL TEXT OR COMMENTS.
Your task:  
Determine if a user query is about one of the following database tables or is a general knowledge-base (KB) question.

Database tables:
1. employees
   Columns: id, name, email, role, team, jira_username
2. jira_tickets
   Columns: id, summary, assignee, status, priority
3. deployments
   Columns: service, version, date, status

Classification rules:
- If the query requests information that can be answered using **only** the columns from a specific table above:
    → Return: route = "db", domain = "<table_name>"
- Otherwise:
    → Return: route = "kb", domain = "general"

Output format (must always be valid JSON):
{
  "route": "<db|kb>",
  "domain": "<table_name|general>",
  "confidence": <float between 0.5 and 1.0>
}

Confidence scoring:
- 1.0 → Clear and direct match to a table's columns  
- 0.5–0.9 → Ambiguous or partially matching

Examples:
- "Show me my open Jira tickets." → {"route": "db", "domain": "jira_tickets", "confidence": 1.0}
- "List recent deployments for the payments service." → {"route": "db", "domain": "deployments", "confidence": 1.0}
- "Who is on-call this week?" → {"route": "kb", "domain": "general", "confidence": 0.7}
"""

def classify_query_with_llm(query:str)-> QueryClassification:
   headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
   payload = {
      "model" : f"meta-llama/{GROQ_LLM_MODEL}",
      "messages":[
         {"role":"system", "content":SYSTEM_PROMPT},
         {"role":"user", "content":query}
      ],
      "temperature": 0.2  # Lower temperature for more deterministic responses
   }
   response = requests.post(GROQ_URL, headers=headers, json=payload)
   response.raise_for_status()
   raw = response.json()["choices"][0]["message"]["content"]
   
   try:
      # Debug the response
      print("RAW RESPONSE:", raw)
      
      # Try to extract JSON if it's embedded in text
      import re
      json_match = re.search(r'\{.*\}', raw, re.DOTALL)
      if json_match:
          raw = json_match.group(0)
      
      data = json.loads(raw)
      print("CLASSIFICATION SUCCESSFUL")
      return{
         "route": data.get("route", "kb"),
         "domain": data.get("domain", None),
         "confidence": data.get("confidence", 0.5),
      }
   except json.JSONDecodeError as e:
      print(f"CLASSIFICATION FAILED: {e}")
      print(f"Raw response was: {raw}")
      return {
         "route": "kb",
         "domain": None,
         "confidence": 0.5
      }
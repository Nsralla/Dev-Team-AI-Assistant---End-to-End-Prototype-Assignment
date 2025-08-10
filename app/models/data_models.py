# create data models for employees using pydantic model 
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from enum import Enum

class Employee(BaseModel):
    id: int
    name: str
    role: str
    email: EmailStr # built in validator
    team: str
    jira_username: str  # This field exists in the JSON
    # Remove jira_ticket as it doesn't exist in the JSON


# Use Literal for a fixed set of string values
class Jira_tickets(BaseModel):
    id: str
    summary: str
    assignee: str # employee jira user name
    status: Literal["Open", "In Progress", "Closed"] 
    priority: str



class DeploymentStatus(str, Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
 
class Deployment(BaseModel):
    service: str
    version: str
    date: datetime
    status: Literal["Success", "Failed"]  # Using Literal instead of Enum for simplicity
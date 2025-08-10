from email.mime import text
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    team = Column(Text)
    jira_username = Column(Text)
    
class JiraTicket(Base):
    __tablename__ = "jira_tickets"
    id = Column(Text, primary_key=True)  # Remove autoincrement for text column
    summary = Column(Text)
    status = Column(Text)
    assignee = Column(Text)
    priority = Column(Text)
    
class Deployment(Base):
    __tablename__ = "deployments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(Text)
    version = Column(Text)
    date = Column(Text)  # Store ISO string
    status = Column(Text)
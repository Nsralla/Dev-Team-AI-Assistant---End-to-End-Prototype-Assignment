import json
import os
import sys
from pathlib import Path
# INSERT JSON FILE TO SQLLITE
# Add the root directory to the Python path so we can import from the root level
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Use absolute import instead of relative import
from models import Employee, JiraTicket, Deployment

# Use the actual data directory path
DATA_DIR = root_dir / "data"
DB_PATH = f"sqlite:///{DATA_DIR}/data_store.db"

# Print paths for debugging
print(f"Root directory: {root_dir}")
print(f"Data directory: {DATA_DIR}")
print(f"Database path: {DB_PATH}")

engine = create_engine(DB_PATH)
# Import the Base and all models
from models import Base, Employee, JiraTicket, Deployment

# Drop all tables and recreate them
print("Dropping all existing tables...")
Base.metadata.drop_all(engine)
print("Creating new tables...")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def load_json(filename):
    file_path = DATA_DIR / filename
    print(f"Loading data from: {file_path}")
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        sys.exit(1)

def load_employees():
    print("Loading employees...")
    employees = load_json("employees.json")
    count = 0
    
    # Create a fresh session for this operation
    emp_session = Session()
    
    for emp in employees:
        try:
            # Check if employee already exists
            existing = emp_session.query(Employee).filter_by(id=emp["id"]).first()
            if existing:
                print(f"Employee with ID {emp['id']} already exists, updating...")
                for key, value in emp.items():
                    setattr(existing, key, value)
            else:
                print(f"Adding employee: {emp['name']}")
                emp_session.add(Employee(**emp))
                count += 1
                
            # Commit after each employee to avoid transaction issues
            emp_session.commit()
        except Exception as e:
            print(f"Error adding employee {emp.get('id', 'unknown')}: {str(e)}")
            emp_session.rollback()  # Roll back on error
    
    emp_session.close()
    print(f"Added {count} new employees")

def load_jira_tickets():
    print("Loading JIRA tickets...")
    tickets = load_json("jira_tickets.json")
    count = 0
    
    # Create a fresh session for this operation
    ticket_session = Session()
    
    for ticket in tickets:
        try:
            # Check if ticket already exists
            existing = ticket_session.query(JiraTicket).filter_by(id=ticket["id"]).first()
            if existing:
                print(f"Ticket with ID {ticket['id']} already exists, updating...")
                for key, value in ticket.items():
                    setattr(existing, key, value)
            else:
                print(f"Adding ticket: {ticket['id']}")
                ticket_session.add(JiraTicket(**ticket))
                count += 1
                
            # Commit after each ticket to avoid transaction issues
            ticket_session.commit()
        except Exception as e:
            print(f"Error adding ticket {ticket.get('id', 'unknown')}: {str(e)}")
            ticket_session.rollback()  # Roll back on error
    
    ticket_session.close()
    print(f"Added {count} new JIRA tickets")

def load_deployments():
    print("Loading deployments...")
    deployments = load_json("deployments.json")
    count = 0
    
    # Create a fresh session for this operation
    dep_session = Session()
    
    for dep in deployments:
        try:
            # Ensure ISO format date string
            if isinstance(dep["date"], str):
                try:
                    datetime.fromisoformat(dep["date"].replace('Z', '+00:00'))
                except ValueError:
                    print(f"Warning: Invalid ISO date: {dep['date']}, attempting to fix...")
                    # Try to parse with datetime
                    try:
                        dt = datetime.strptime(dep["date"], "%Y-%m-%dT%H:%M:%SZ")
                        dep["date"] = dt.isoformat()
                    except ValueError:
                        print(f"Error: Could not parse date: {dep['date']}")
                        continue
            
            print(f"Adding deployment: {dep['service']} {dep['version']}")
            # Create new deployment record
            dep_session.add(Deployment(**dep))
            count += 1
            
            # Commit after each deployment to avoid transaction issues
            dep_session.commit()
        except Exception as e:
            print(f"Error adding deployment for {dep.get('service', 'unknown')}: {str(e)}")
            dep_session.rollback()  # Roll back on error
    
    dep_session.close()
    print(f"Added {count} new deployments")

if __name__ == "__main__":
    try:
        print("Starting data loading process...")
        
        # Use separate sessions for each data type to avoid transaction conflicts
        load_employees()
        print("Employees loaded successfully!")
        
        load_jira_tickets()
        print("JIRA tickets loaded successfully!")
        
        load_deployments()
        print("Deployments loaded successfully!")
        
        print("All data loaded successfully!")
    except Exception as e:
        print(f"Error during data loading: {str(e)}")
    finally:
        print("Database operations completed.")

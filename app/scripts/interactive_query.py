import sys
from pathlib import Path
import sqlite3

# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Database path
DATA_DIR = root_dir / "data"
DB_PATH = DATA_DIR / "data_store.db"

def execute_query(query, params=None):
    """Execute a query and print the results"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names and results
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        results = cursor.fetchall()
        
        # Print the results
        print(f"\nResults: {len(results)} rows")
        
        if column_names and results:
            # Print column headers
            header = " | ".join(column_names)
            separator = "-" * len(header)
            print(separator)
            print(header)
            print(separator)
            
            # Print rows
            for row in results:
                print(" | ".join(str(item) for item in row))
            print(separator)
        
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def interactive_mode():
    """Run in interactive mode allowing user to input custom SQL queries"""
    print(f"\n=== Interactive SQL Query Tool ===")
    print(f"Database: {DB_PATH}")
    print("Type 'exit' or 'quit' to exit.")
    print("Available tables: employees, jira_tickets, deployments")
    print("Example: SELECT * FROM employees WHERE team = 'Backend'")
    
    while True:
        query = input("\nEnter SQL query: ").strip()
        
        if query.lower() in ('exit', 'quit'):
            print("Exiting interactive mode.")
            break
        
        if not query:
            continue
        
        execute_query(query)

if __name__ == "__main__":
    interactive_mode()

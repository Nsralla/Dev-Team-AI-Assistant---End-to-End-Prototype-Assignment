import sys
from pathlib import Path
import sqlite3
#  execute pre defined queries
# Add the root directory to the Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Database path
DATA_DIR = root_dir / "data"
DB_PATH = DATA_DIR / "data_store.db"

print(f"Connecting to database at: {DB_PATH}")

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
        print(f"\nQuery: {query}")
        print(f"Results: {len(results)} rows")
        
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

def count_records(table_name):
    """Count records in a table"""
    query = f"SELECT COUNT(*) FROM {table_name}"
    execute_query(query)

def main():
    """Main function to run sample queries"""
    print("\n=== Database Query Tool ===\n")
    
    # Count records in each table
    print("\n=== Record Counts ===")
    count_records("employees")
    count_records("jira_tickets")
    count_records("deployments")
    
    # Query employees
    print("\n=== All Employees ===")
    execute_query("SELECT * FROM employees")
    
    # Query JIRA tickets
    print("\n=== All JIRA Tickets ===")
    execute_query("SELECT * FROM jira_tickets")
    
    # Query deployments
    print("\n=== All Deployments ===")
    execute_query("SELECT * FROM deployments")
    
    # Example of a more complex query - Employees with their assigned JIRA tickets
    print("\n=== Employees with JIRA Tickets ===")
    execute_query("""
        SELECT e.name, e.role, e.team, j.id as ticket_id, j.summary, j.status, j.priority
        FROM employees e
        LEFT JOIN jira_tickets j ON e.jira_username = j.assignee
        ORDER BY e.name
    """)
    
    # Example of filtering - High priority tickets
    print("\n=== High Priority Tickets ===")
    execute_query("SELECT * FROM jira_tickets WHERE priority = 'High' OR priority = 'Critical'")
    
    # Example of filtering - Failed deployments
    print("\n=== Failed Deployments ===")
    execute_query("SELECT * FROM deployments WHERE status = 'Failed'")

if __name__ == "__main__":
    main()

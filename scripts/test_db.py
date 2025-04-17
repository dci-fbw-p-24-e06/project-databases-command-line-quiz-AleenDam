from db import connect_db
from questions import create_initial_tables, get_topics

# Test database connection
def test_db_connection():
    try:
        conn = connect_db()
        print("Database connection successful!")
        
        # Create initial tables if they don't exist
        create_initial_tables()
        print("Initial tables created successfully!")
        
        # Get topics
        topics = get_topics()
        print(f"Available topics: {topics}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()
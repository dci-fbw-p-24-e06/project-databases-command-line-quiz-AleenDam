import psycopg2 as pg
from psycopg2 import sql
from config import config

def connect_db():
    """Establish a connection to the PostgreSQL database."""
    return pg.connect(**config)

def execute_query(query, params=None):
    """Executes a query on the database and returns the result."""
    conn = connect_db()  # Establish a connection
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    result = cursor.fetchall()  # Fetch the result
    conn.commit()  # Commit the transaction
    cursor.close()  # Close the cursor
    conn.close()  # Close the connection
    return result


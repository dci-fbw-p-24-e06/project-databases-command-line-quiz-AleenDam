import psycopg2 as pg
from config import config

def create_database():
    """
    Connects to the PostgreSQL server and creates a new
    database 'quiz_db'.

    Args:
        database (str): The name of the database to create.
        config (dict): The configuration settings for the database.
    Returns:
        bool: True if the database was created successfully, False otherwise.
    """

    try:
        # Connect to an existing database 'postgres' to create a new database
        conn_params = {**config, 'dbname': 'postgres'}
        conn = pg.connect(**conn_params)
        conn.autocommit = True # Disable transaction block for create database command
            
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {config['dbname']};")
            print(f"☺️ Database '{config['dbname']}' created successfully.")
            return True
            
    except pg.errors.DuplicateDatabase:
        # If the database already exists, handle the error
        print("❌ Database 'quiz_db' already exists.")
        return "Database already exists."
    
    except (Exception, pg.DatabaseError) as e:
        print(f"Error creating database: {e}")
        return f"Error: {e}"
    
create_database()

# sudo -u postgres psql
# \l
# psql -U aleen -d quiz_db -h localhost





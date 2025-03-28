import psycopg2 as pg
from config import config

def create_database():
    """
    Connects to PostgreSQL to create the quiz database.
    """
    try:
        # Connect to the 'postgres' database (default database)
        conn_params = {**config, 'dbname': 'postgres'}
        conn = pg.connect(**conn_params)
        conn.autocommit = True  # Disable transaction block for database creation
        cursor = conn.cursor()

        # Create the 'quiz_db' database if it doesn't exist
        cursor.execute(f"CREATE DATABASE {config['dbname']};")
        print(f"☺️ Database '{config['dbname']}' created successfully.")
        
        conn.close()

    except pg.errors.DuplicateDatabase:
        print(f"❌ Database '{config['dbname']}' already exists.")
    
    except Exception as e:
        print(f"Error creating database: {e}")

def create_topic_table(topic):
    """
    Creates a table for the specified topic if it doesn't already exist.
    """
    conn = pg.connect(**config)
    cursor = conn.cursor()

    # SQL query to create a table for a topic
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {topic} (
        id SERIAL PRIMARY KEY,
        module TEXT,
        submodule TEXT,
        difficulty INT CHECK (difficulty BETWEEN 1 AND 3),
        question TEXT,
        correct_answer TEXT,
        wrong_answer1 TEXT,
        wrong_answer2 TEXT,
        wrong_answer3 TEXT,
        wrong_answer4 TEXT,
        wrong_answer5 TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    print(f"☺️ Table for topic '{topic}' created successfully.")
    conn.close()

if __name__ == "__main__":
    # Create the database and the necessary tables
    create_database()
    topics = ["geography", "history", "literature", "languages", "general_knowledge"]
    for topic in topics:
        create_topic_table(topic)



# sudo -u postgres psql
# \l
# psql -U aleen -d quiz_db -h localhost





import psycopg2 as pg
from config import config
from psycopg2 import sql

def connect_db():
    """
    Establish a connection to the PostgreSQL database.
    """
    conn = pg.connect(**config)
    return conn

def create_topic_table(conn, topic_name):
    """
    Creates a new table for the given topic dynamically.
    """
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                module TEXT NOT NULL,
                submodule TEXT NOT NULL,
                difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                wrong_answer1 TEXT NOT NULL,
                wrong_answer2 TEXT NOT NULL,
                wrong_answer3 TEXT,
                wrong_answer4 TEXT,
                wrong_answer5 TEXT
            );
        """).format(sql.Identifier(topic_name)))
        conn.commit()
        print(f"☺️ Table for topic '{topic_name}' created successfully.")


def add_topic():
    """
    Allows the user to add a new topic.
    """
    topic_name = input("Enter the new topic name: ").lower()
    conn = connect_db()

    # Check if the topic already exists
    with conn.cursor() as cursor:
        cursor.execute("SELECT topic_name FROM topics WHERE topic_name = %s", (topic_name,))
        existing_topic = cursor.fetchone()

        if existing_topic:
            print(f"❌ Topic '{topic_name}' already exists.")
        else:
            # Insert the new topic into the 'topics' table
            cursor.execute("INSERT INTO topics (topic_name) VALUES (%s)", (topic_name,))
            conn.commit()
            print(f"☺️ Topic '{topic_name}' added successfully.")
            create_topic_table(conn, topic_name)
    conn.close()

if __name__ == "__main__":
    add_topic()

import psycopg2 as pg
from psycopg2 import sql
from config import config

def connect_db():
    """Establish a connection to the PostgreSQL database."""
    return pg.connect(**config)

def create_initial_tables():
    """Creates initial tables for topics, questions, and scores if they don't exist."""
    conn = connect_db()
    with conn.cursor() as cursor:
        # Create topics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic_name TEXT PRIMARY KEY
            );
        """)
        
        # Create scores table with 'topic_name' column directly
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                score INT NOT NULL,
                FOREIGN KEY (topic_name) REFERENCES topics(topic_name) ON DELETE CASCADE
            );
        """)
        
        # Create sample tables for each topic dynamically (languages, history, literature)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS languages (
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
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
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
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS literature (
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
        """)

        conn.commit()
    conn.close()

def get_topics():
    """Fetches all available topics from the database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT topic_name FROM topics;")
        topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics

def get_questions(topic, limit=5):
    """Fetches random questions for a given topic."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("SELECT question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, wrong_answer5 FROM {} ORDER BY RANDOM() LIMIT %s;").format(
            sql.Identifier(topic)), [limit])  # Correct way to pass parameters in SQL query
        questions = cursor.fetchall()
    conn.close()
    return questions

def save_score(username, topic, score):
    """Saves the user's score into the database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO scores (username, topic_name, score) 
            VALUES (%s, %s, %s);
        """, (username, topic, score))
        conn.commit()
    conn.close()

def add_topic(topic_name):
    """Adds a new topic to the database."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT topic_name FROM topics WHERE topic_name = %s", (topic_name,))
        if cursor.fetchone():
            print("❌ Topic already exists.")
        else:
            cursor.execute("INSERT INTO topics (topic_name) VALUES (%s)", (topic_name,))
            conn.commit()
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
            """
            ).format(sql.Identifier(topic_name)))
            conn.commit()
            print(f"✅ Topic '{topic_name}' added successfully!")
    conn.close()

def add_question(topic, module, submodule, difficulty, question, correct_answer, wrong_answers):
    """Adds a question to an existing topic."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            INSERT INTO {} (module, submodule, difficulty, question, correct_answer, 
            wrong_answer1, wrong_answer2, wrong_answer3) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        ).format(sql.Identifier(topic)),
        (module, submodule, difficulty, question, correct_answer, *wrong_answers))
        conn.commit()
        print("✅ Question added successfully!")
    conn.close()

def create_user(username, password):
    """Creates a new user with the provided username and password."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("❌ User already exists.")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            print(f"✅ User '{username}' created successfully!")
    conn.close()

def authenticate_user(username, password):
    """Authenticates a user based on username and password."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        stored_password = cursor.fetchone()
    conn.close()

    if stored_password and stored_password[0] == password:
        return True
    return False

def view_scores(username):
    """Fetches and displays the user's scores."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT topic_name, AVG(score) AS average_score
            FROM scores
            WHERE username = %s
            GROUP BY topic_name;
        """, (username,))
        scores = cursor.fetchall()
    conn.close()
    return scores


def add_hardcoded_questions():
    """Populates the topics tables with hardcoded questions and answers."""
    # Define the hardcoded questions for each topic
    topics_data = {
        "languages": [
            ("What is the official language of Brazil?", "Portuguese", "Spanish", "French", "English", "Italian", "German"),
            ("Which language is spoken in Japan?", "Japanese", "Chinese", "Korean", "Vietnamese", "Mandarin", "Thai", ""),
            ("Which language is widely spoken in India?", "Hindi", "Bengali", "Marathi", "Gujarati", "Punjabi", "Tamil", ""),
            ("What is the official language of the United Kingdom?", "English", "Welsh", "Scots Gaelic", "French", "Dutch", "German", ""),
            ("Which language is primarily spoken in Brazil?", "Portuguese", "Spanish", "French", "Italian", "English", "Dutch", "German")
        ],
        "history": [
            ("Who was the first president of the United States?", "George Washington", "Abraham Lincoln", "Thomas Jefferson", "Andrew Jackson", "John Adams", ""),
            ("In which year did World War II end?", "1945", "1939", "1918", "1965", "1950", ""),
            ("Who discovered America?", "Christopher Columbus", "Vasco da Gama", "Marco Polo", "Ferdinand Magellan", "Amerigo Vespucci", ""),
            ("Who was the first man to walk on the moon?", "Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin", "Michael Collins", "John Glenn", ""),
            ("Which country was formerly known as Persia?", "Iran", "Iraq", "Afghanistan", "Syria", "Turkey", "")
        ],
        "literature": [
            ("Who wrote '1984'?", "George Orwell", "Aldous Huxley", "Ray Bradbury", "Ernest Hemingway", "Mark Twain", ""),
            ("Which book starts with the phrase 'Call me Ishmael'?", "Moby-Dick", "The Great Gatsby", "Pride and Prejudice", "To Kill a Mockingbird", "The Catcher in the Rye", ""),
            ("Who is the author of 'Romeo and Juliet'?", "William Shakespeare", "Jane Austen", "Charles Dickens", "Leo Tolstoy", "Homer", ""),
            ("Who wrote 'War and Peace'?", "Leo Tolstoy", "Fyodor Dostoevsky", "Anton Chekhov", "Ivan Turgenev", "Victor Hugo", ""),
            ("What is the first book in the 'Harry Potter' series?", "Harry Potter and the Sorcerer's Stone", "Harry Potter and the Chamber of Secrets", "Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire", "Harry Potter and the Order of the Phoenix", "")
        ]
    }

    conn = connect_db()
    with conn.cursor() as cursor:
        for topic, questions in topics_data.items():
            # First, add the topic to the 'topics' table
            cursor.execute("INSERT INTO topics (topic_name) VALUES (%s) ON CONFLICT (topic_name) DO NOTHING;", (topic,))
            
            # Now add the questions for each topic
            for question_data in questions:
                # Debug: Print the question_data to check its size
                print(f"question_data: {question_data}")

                # Ensure there are exactly 7 elements in the question_data tuple
                if len(question_data) != 7:
                    print(f"❌ Invalid number of elements in question_data: {question_data}")
                    continue  # Skip this question if it doesn't have 7 elements
                
                question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, wrong_answer5 = question_data
                cursor.execute(sql.SQL("""
                    INSERT INTO {} (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, wrong_answer5)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """).format(sql.Identifier(topic)), (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, wrong_answer5))
            conn.commit()
    conn.close()
    print("✅ Hardcoded questions added successfully!")

from db import connect_db
import psycopg2
from psycopg2 import sql


# Topic management functions
def create_initial_tables():
    """Creates initial tables for topics, questions, and scores if they don't exist."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic_name TEXT PRIMARY KEY
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                score INT NOT NULL,
                FOREIGN KEY (topic_name) REFERENCES topics(topic_name) ON DELETE CASCADE
            );
        """)
        
        topics = ["languages", "history", "literature", "general", "geography"]
        for topic in topics:
            # Drop the topic table if it exists
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(topic)))
            
            # Recreate the topic table
            cursor.execute(sql.SQL("""
                CREATE TABLE {} (
                    id SERIAL PRIMARY KEY,
                    difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
                    question TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    wrong_answer1 TEXT NOT NULL,
                    wrong_answer2 TEXT NOT NULL,
                    wrong_answer3 TEXT,
                    wrong_answer4 TEXT
                );
            """).format(sql.Identifier(topic)))

        
    conn.commit()
    conn.close()
    
    # Populate tables with hardcoded questions
    add_hardcoded_questions()

def get_topics():
    """Fetches all available topics from the database and returns a mapping of display to raw names."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT topic_name FROM topics")
        topics_from_db = cursor.fetchall()
    conn.close()

    topic_mapping = {}
    for topic in topics_from_db:
        raw_name = topic[0].strip().lower()  # The raw name for the database
        display_name = raw_name.replace("_", " ").title()  # User-friendly name for display
        topic_mapping[display_name] = raw_name

    return topic_mapping  # Return a dictionary like {"Languages": "languages"}


def delete_topic_from_db(topic_name):
    try:
        # Normalize the topic_name to lowercase for comparison
        normalized_topic_name = topic_name.strip().lower()

        conn = connect_db()
        with conn.cursor() as cursor:
            # Check if the topic exists in the database, normalized to lowercase
            cursor.execute("SELECT topic_name FROM topics WHERE LOWER(topic_name) = %s", (normalized_topic_name,))
            topic = cursor.fetchone()

            if topic:
                # Deleting the topic from the 'topics' table
                cursor.execute("DELETE FROM topics WHERE LOWER(topic_name) = %s", (normalized_topic_name,))
                print(f"Topic '{topic_name}' deleted from the topics table.")

                # Drop the associated table (sanitize topic name to avoid SQL injection)
                sanitized_topic_name = normalized_topic_name.replace(" ", "_")
                cursor.execute(f"DROP TABLE IF EXISTS {sanitized_topic_name}")
                print(f"Table '{sanitized_topic_name}' has been dropped.")

                conn.commit()
            else:
                print(f"No topic found with name '{topic_name}' in the topics table.")

        # After deletion, update and show the list of topics
        updated_topics = get_topics()  # Get the updated list
        print("Updated list of topics:")
        for topic in updated_topics:
            print(topic)  # Show the updated list

    except Exception as e:
        print(f"❌ An error occurred while deleting the topic: {e}")
    
    finally:
        if conn:
            conn.close()  # Ensure the connection is closed



def show_topics(topics):
    """Display the list of topics."""
    print("\nUpdated list of topics:")
    for idx, topic in enumerate(topics, 1):
        print(f"{idx}. {topic}")



def add_topic(topic_name):
    """Adds a new topic to the database and creates a corresponding table."""
    topic_name_normalized = topic_name.strip().lower().replace(" ", "_")  # Normalize topic name

    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            # Check if the topic already exists
            cursor.execute("SELECT topic_name FROM topics WHERE topic_name = %s", (topic_name_normalized,))
            if cursor.fetchone():
                print("❌ Topic already exists.")
            else:
                # Insert the topic into the 'topics' table
                cursor.execute("INSERT INTO topics (topic_name) VALUES (%s)", (topic_name_normalized,))
                conn.commit()

                # Create a table for the topic with the normalized topic name
                cursor.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {} (
                        id SERIAL PRIMARY KEY,
                        difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
                        question TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        wrong_answer1 TEXT NOT NULL,
                        wrong_answer2 TEXT NOT NULL,
                        wrong_answer3 TEXT,
                        wrong_answer4 TEXT
                    );
                """).format(sql.Identifier(topic_name_normalized)))
                conn.commit()

                print(f"✅ Topic '{topic_name}' added successfully!")

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()


def get_questions(topic, difficulty=None):
    """Fetches all questions from the selected topic and optional difficulty."""
    # Convert topic to lowercase and replace spaces with underscores for table naming
    table_name = topic.lower().replace(" ", "_")

    conn = connect_db()
    with conn.cursor() as cursor:
        if difficulty:
            cursor.execute(sql.SQL("""
                SELECT question, correct_answer, wrong_answer1, wrong_answer2, 
                       wrong_answer3, wrong_answer4, difficulty
                FROM {table}
                WHERE difficulty = %s
                ORDER BY RANDOM();  -- Shuffle questions
            """).format(table=sql.Identifier(table_name)), (difficulty,))
        else:
            cursor.execute(sql.SQL("""
                SELECT question, correct_answer, wrong_answer1, wrong_answer2, 
                       wrong_answer3, wrong_answer4, difficulty
                FROM {table}
                ORDER BY RANDOM();  -- Shuffle questions
            """).format(table=sql.Identifier(table_name)))
        
        questions = cursor.fetchall()

    conn.close()

    return questions



def validate_question_data(question_data):
    """Validates the question data format before inserting into the database."""
    if len(question_data) < 5:
        print(f"❌ Invalid question data: {question_data}. Expected 5 elements (question, correct answer, and at least 3 wrong answers).")
        return False
    while len(question_data) < 6:
        question_data.append('')
    question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4 = question_data
    if not question or not correct_answer or not wrong_answer1 or not wrong_answer2 or not wrong_answer3 or not wrong_answer4:
        print(f"❌ Invalid question data: {question_data}")
        return False
    if len(question) > 255 or len(correct_answer) > 255 or len(wrong_answer1) > 255:
        print(f"❌ Invalid question data: {question_data}")
        return False
    return True


def add_questions(topic_name, difficulty, question, correct_answer, wrong_answers):
    """Adds a new question to the specified topic table."""
    topic_name_normalized = topic_name.strip().lower().replace(" ", "_")  # Ensure consistency

    conn = connect_db()
    with conn.cursor() as cursor:
        try:
            # Ensure the table for the topic exists (it should have been created previously)
            cursor.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
                    question TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    wrong_answer1 TEXT NOT NULL,
                    wrong_answer2 TEXT NOT NULL,
                    wrong_answer3 TEXT,
                    wrong_answer4 TEXT
                );
            """).format(sql.Identifier(topic_name_normalized)))
            conn.commit()

            # Insert the new question into the topic-specific table
            cursor.execute(sql.SQL("""
                INSERT INTO {} (difficulty, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """).format(sql.Identifier(topic_name_normalized)),
                           (difficulty, question, correct_answer, wrong_answers[0], wrong_answers[1], wrong_answers[2], wrong_answers[3]))

            conn.commit()
            print("✅ Question added successfully!")

        except psycopg2.Error as e:
            print(f"❌ Error: {e}")
        finally:
            conn.close()


# Score management functions
def save_score(username, topic, score):
    """Saves the user's score into the database, updating if a record already exists."""
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO scores (username, topic_name, score)
                VALUES (%s, %s, %s)
                ON CONFLICT (username, topic_name)
                DO UPDATE SET score = EXCLUDED.score;
            """, (username, topic, score))
            conn.commit()
        conn.close()
        print(f"Score saved successfully!")
    except Exception as e:
        print(f"❌ Error saving score: {e}")



def view_scores(user):
    """Fetch the average scores for a user across topics."""
    try:
        connection = connect_db()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT topic_name, AVG(score) as avg_score
            FROM scores
            WHERE username = %s
            GROUP BY topic_name
            ORDER BY avg_score DESC
        """, (user,))
        
        scores = cursor.fetchall()
        connection.close()
        
        return scores if scores else None
    except Exception as e:
        print(f"❌ Error fetching scores: {e}")
        return None

def get_all_user_scores():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, topic_name, AVG(score)::numeric(5,2) AS average_score
        FROM scores
        GROUP BY username, topic_name
        ORDER BY average_score DESC;
    """)

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

def get_top_user():
    conn = connect_db()
    cur = conn.cursor()

    # Query to get the user with the highest average score
    cur.execute("""
        SELECT username, AVG(score)::numeric(5,2) AS avg_score
        FROM scores
        GROUP BY username
        ORDER BY avg_score DESC
        LIMIT 1;
    """)

    winner = cur.fetchone()

    cur.close()
    conn.close()

    return winner

# Topic validation function
def validate_topic_table(topic):
    """Validate that a table has the correct structure for a quiz topic."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s;
        """, (topic,))
        columns = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    required_columns = {'difficulty', 'question', 'correct_answer', 'wrong_answer1', 'wrong_answer2', 'wrong_answer3', 'wrong_answer4'}
    return required_columns.issubset(columns)

def create_topic_table(topic):
    """Creates a table for a given topic with the necessary structure."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                wrong_answer1 TEXT NOT NULL,
                wrong_answer2 TEXT NOT NULL,
                wrong_answer3 TEXT,
                wrong_answer4 TEXT
            );
        """).format(sql.Identifier(topic)))
        conn.commit()
    conn.close()
# Hardcoded question population functions

def add_hardcoded_questions():
    """Populates the topics tables with hardcoded questions and answers."""
    topics_data = {
        "languages": [
            (1, "What is the official language of Brazil?", "Portuguese", "Spanish", "French", "English", "Brazilian"),
            (1, "Which language is spoken in Japan?", "Japanese", "Chinese", "Korean", "Vietnamese", "Tagalog"),
            (1, "Which language is widely spoken in India?", "Hindi", "Bengali", "Marathi", "Gujarati", "Punjabi"),
            (2, "What is the official language of the United Kingdom?", "English", "Welsh", "Scots Gaelic", "Dutch", "French"),
            (2, "Which language is primarily spoken in Columbia?", "Spanish", "Portuguese", "Italian", "English", "Dutch"),
            (2, "What is the official language of Argentina?", "Spanish", "Portuguese", "English", "Italian", "German"),
            (3, "Which language is spoken in Brazil and parts of the Caribbean?", "Portuguese", "Spanish", "French", "Italian", "Dutch"),
            (3, "Which language is primarily spoken in Iceland?", "Icelandic", "Norwegian", "Danish", "Swedish", "Finnish"),
            (3, "Which language is spoken in Finland?", "Finnish", "Swedish", "Norwegian", "Danish", "Estonian")
        ],
        "history": [
            (1, "Who was the first president of the United States?", "George Washington", "Abraham Lincoln", "Thomas Jefferson", "Andrew Jackson", "John Adams"),
            (1, "Who was the first emperor of Rome?", "Augustus", "Julius Caesar", "Nero", "Tiberius", "Caligula"),
            (2, "In which year did World War II end?", "1945", "1939", "1918", "1965", "1950"),
            (2, "Who discovered America?", "Christopher Columbus", "Vasco da Gama", "Marco Polo", "Ferdinand Magellan", "Amerigo Vespucci"),
            (2, "Who was the first man to walk on the moon?", "Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin", "Michael Collins", "John Glenn"),
            (3, "Which country was formerly known as Persia?", "Iran", "Iraq", "Afghanistan", "Syria", "Turkey"),
            (3, "Who was the first president of South Africa?", "Nelson Mandela", "Thabo Mbeki", "Jacob Zuma", "F.W. de Klerk", "Hendrik Verwoerd"),
            (3, "In which year did the Titanic sink?", "1912", "1905", "1898", "1923", "1910")
        ],
        "literature": [
            (1, "Who wrote 'To Kill a Mockingbird'?", "Harper Lee", "Mark Twain", "Jane Austen", "F. Scott Fitzgerald", "J.K. Rowling"),
            (1, "Which novel features the character of Sherlock Holmes?", "The Hound of the Baskervilles", "The Great Gatsby", "Pride and Prejudice", "Moby Dick", "1984"),
            (1, "Who wrote '1984'?", "George Orwell", "Aldous Huxley", "J.K. Rowling", "Charles Dickens", "Ernest Hemingway"),
            (2, "In which year was 'Harry Potter and the Sorcerer's Stone' published?", "1997", "1995", "2000", "1999", "2005"),
            (2, "Who is the author of 'The Catcher in the Rye'?", "J.D. Salinger", "Ernest Hemingway", "F. Scott Fitzgerald", "Mark Twain", "John Steinbeck"),
            (2, "Who wrote 'The Great Gatsby'?", "F. Scott Fitzgerald", "Ernest Hemingway", "J.D. Salinger", "Mark Twain", "Charles Dickens"),
            (3, "Who wrote 'One Hundred Years of Solitude'?", "Gabriel García Márquez", "Isabel Allende", "Mario Vargas Llosa", "Carlos Fuentes", "Jorge Luis Borges"),
            (3, "Which novel is set during the time of the American Civil War?", "Gone with the Wind", "Moby Dick", "Pride and Prejudice", "War and Peace", "The Scarlet Letter"),
            (3, "Who wrote 'Crime and Punishment'?", "Fyodor Dostoevsky", "Leo Tolstoy", "Anton Chekhov", "Vladimir Nabokov", "Alexander Pushkin")
        ]}
    conn = connect_db()
    with conn.cursor() as cursor:
        for topic, questions in topics_data.items():
            # Create the table for the topic if it doesn't exist
            create_topic_table(topic)

            # Insert the questions into the topic table
            for question in questions:
                # Ensure the question has 7 elements before inserting
                if len(question) == 7:
                    cursor.execute(sql.SQL("""
                        INSERT INTO {} (difficulty, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """).format(sql.Identifier(topic)), question)
                else:
                    print(f"❌ Invalid question data: {question} for topic: {topic}")

    conn.commit()
    print("✅ Hardcoded topics and questions added successfully!")
    conn.close()







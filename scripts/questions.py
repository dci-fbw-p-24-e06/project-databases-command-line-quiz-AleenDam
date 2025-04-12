import psycopg2 as pg
from psycopg2 import sql
from config import config


# Database connection functions
def connect_db():
    """Establish a connection to the PostgreSQL database."""
    return pg.connect(**config)


# User management functions
def create_user_account():
    """Registers a new user account in the PostgreSQL database."""
    username = input("Choose a username: ").strip()

    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("❌ Username already exists. Please choose a different one.")
            conn.close()
            return None  # Optionally, return None to allow retry

        password = input("Choose a password: ").strip()

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        print(f"✅ User '{username}' registered successfully!")
    
    conn.close()
    return username


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
        
        topics = ["languages", "history", "literature", "general_knowledge", "geography"]
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
    """Fetches all available topics from the database and filters with known topics."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT topic_name
            FROM topics
        """)
        topics_from_db = cursor.fetchall()

    conn.close()

    # List of known topics in lowercase
    known_topics = ['languages', 'history', 'literature', 'general_knowledge', 'geography']

    topics = []
    for topic in topics_from_db:
        topic_name = topic[0].strip().lower()  # Strip any extra spaces and convert to lowercase

        if topic_name in known_topics:
            # Capitalize for proper display
            topics.append(topic_name.title())  # `title()` capitalizes each word in multi-word topics

    return topics


def add_topic(topic_name):
    """Adds a new topic to the database."""
    topic_name = topic_name.strip().lower().replace(" ", "_")  # Normalize topic name

    conn = connect_db()
    with conn.cursor() as cursor:
        # Check if the topic already exists
        cursor.execute("SELECT topic_name FROM topics WHERE topic_name = %s", (topic_name,))
        if cursor.fetchone():
            print("❌ Topic already exists.")
        else:
            # Insert the topic into the 'topics' table
            cursor.execute("INSERT INTO topics (topic_name) VALUES (%s)", (topic_name,))
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
            """).format(sql.Identifier(topic_name)))
            conn.commit()
            print(f"✅ Topic '{topic_name}' added successfully!")
    conn.close()



def get_questions(topic, difficulty):
    """Fetches questions from the selected topic and difficulty level."""
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            SELECT question, correct_answer, wrong_answer1, wrong_answer2, 
                   wrong_answer3, wrong_answer4
            FROM {} 
            WHERE difficulty = %s
            ORDER BY RANDOM()
            LIMIT 10;
        """).format(sql.Identifier(topic)), (difficulty,))
        questions = cursor.fetchall()

    conn.close()

    return questions


def add_question(topic, difficulty, question, correct_answer, wrong_answers):
    """Adds a question to an existing topic."""
    # Convert question_data to a list so it can be modified (e.g., adding empty wrong answers)
    question_data = [question, correct_answer, *wrong_answers]  # Prepare data as a list
    
    # Validate the question data
    if not validate_question_data(question_data):
        return  # Return if the data is invalid
    
    # Database connection and insertion
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("""
            INSERT INTO {} (difficulty, question, correct_answer, 
            wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """).format(sql.Identifier(topic)),
        (difficulty, *question_data))  # Insert the question using unpacked list data
        conn.commit()
        print("✅ Question added successfully!")
    conn.close()


def validate_question_data(question_data):
    """Validates the question data format before inserting into the database."""
    
    # Ensure there are at least 5 elements (question, correct answer, and 4 wrong answers)
    if len(question_data) < 5:
        print(f"❌ Invalid question data: {question_data}. Expected 5 elements (question, correct answer, and at least 3 wrong answers).")
        return False

    # Add empty strings for any missing wrong answers
    while len(question_data) < 6:
        question_data.append('')  # Add empty string for any missing wrong answer
    
    # Unpack the values
    question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4 = question_data

    # Check if any field is empty
    if not question or not correct_answer or not wrong_answer1 or not wrong_answer2 or not wrong_answer3 or not wrong_answer4:
        print(f"❌ Invalid question data: {question_data}")
        return False

    # Check if question is not too long or too short (optional, just an example)
    if len(question) > 255 or len(correct_answer) > 255 or len(wrong_answer1) > 255:
        print(f"❌ Invalid question data: {question_data}")
        return False

    return True


def delete_topic(topic_name):
    """Deletes the topic from the topics table and drops the corresponding topic table."""
    conn = connect_db()
    with conn.cursor() as cursor:
        try:
            # Delete from the topics list
            cursor.execute("DELETE FROM topics WHERE topic_name = %s", (topic_name.lower(),))

            # Drop the topic table (assumes table name = topic_name.lower())
            table_name = topic_name.lower()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error deleting topic: {e}")
        finally:
            conn.close()

# Score management functions
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


# Hardcoded question population functions

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
        ],
        "general_knowledge": [
            (1, "What is the capital of France?", "Paris", "London", "Berlin", "Madrid", "Rome"),
            (1, "Which planet is known as the Red Planet?", "Mars", "Venus", "Earth", "Jupiter", "Saturn"),
            (1, "What is the largest ocean on Earth?", "Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Southern Ocean", "Arctic Ocean"),
            (2, "Who invented the telephone?", "Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Albert Einstein", "Benjamin Franklin"),
            (2, "What is the smallest country in the world?", "Vatican City", "Monaco", "San Marino", "Liechtenstein", "Nauru"),
            (2, "What is the largest island in the world?", "Greenland", "Australia", "New Guinea", "Borneo", "Madagascar"),
            (3, "Which inventor is known for creating the first successful airplane?", "Wright Brothers", "Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Elon Musk"),
            (3, "Which company created the first personal computer?", "Apple", "IBM", "Microsoft", "Compaq", "HP"),
            (3, "What year did the first manned mission to Mars occur?", "Not yet", "2025", "2030", "2020", "2040")
        ],
        "geography": [
            (1, "What is the largest continent?", "Asia", "Africa", "Europe", "North America", "Australia"),
            (1, "Which country has the most population?", "China", "India", "USA", "Indonesia", "Brazil"),
            (1, "Which country is known as the Land of the Rising Sun?", "Japan", "South Korea", "China", "Thailand", "India"),
            (2, "What is the longest river in the world?", "Nile River", "Amazon River", "Yangtze River", "Mississippi River", "Ganges River"),
            (2, "What is the largest desert in the world?", "Sahara Desert", "Gobi Desert", "Kalahari Desert", "Arabian Desert", "Atacama Desert"),
            (2, "Which is the smallest country in Asia?", "Maldives", "Singapore", "Bhutan", "Nepal", "Sri Lanka"),
            (3, "Which is the largest country by area?", "Russia", "Canada", "United States", "China", "Brazil"),
            (3, "Which country is the largest producer of coffee?", "Brazil", "Vietnam", "Colombia", "Indonesia", "Ethiopia"),
            (3, "Which country is known for the ancient pyramids?", "Egypt", "Mexico", "Peru", "India", "China")
        ]
    }

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







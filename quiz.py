import psycopg2 as pg
import random
from config import config

# Database connection settings
def connect_db():
    """
    Establishes a connection to PostgreSQL database
    using the config dictionary.
    Returns:
        tuple: A connection object and a cursor object,
        or (None, None) if connection fails.
    """

    try:
        with pg.connect(**config) as conn:
            with conn.cursor() as cursor:
                print("🗃️ Connected to the PostgreSQL database ✅")
                return conn, cursor
                     
    except (Exception, pg.DatabaseError) as error:
        print("Error while connecting to PostgreSQL ❌", error)
        return None, None


def show_menu():
    """
    Displays the main menu with options for the quiz application.
    """

    print("\n🎲 Quiz Game")
    print("1. Play a quiz")
    print("2. Add a new question")
    print("6. Exit")


def get_topics():
    """
    Retrieves a list of available topics from the database.

    Args:
        cursor (pg.cursor): Database cursor

    Returns:
        list: A list of available topic names.
    """

    conn, cursor = connect_db()
    if conn is None:
        return []

    cursor.execute("SELECT name FROM topics")
    """
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    rows = cursor.fetchall()
    # conn.close
    return [row[0] for row in rows]


def take_quiz(cursor):
    """
    Takes a quiz for a selected topic from the user.

    Args:
        cursor (pg.cursor): Database cursor"
    """

    topics = get_topics(cursor)
    if not topics:
        print("No topics found. Please add some topics first.")
        return
    
    print("\nAvailable topics:")
    for idx, topic in enumerate(topics, 1):
        print(f"{idx}. {topic}")

    try:
        choice = int(input("Select a topic number:")) - 1  # number of topics
        if 0 <= choice < len(topics):
            topic = topics[choice]
            start_quiz(cursor, topic)
        else:
            print("😔 Invalid topic number. Please try again.")
    except ValueError:
        print("�� Invalid selection. Please try again.")


def start_quiz(cursor, topic):
    """
    Fetches random questions from the selected topic
    and starts the quiz.

    Args:
        cursor (pg.cursor): Database cursor
        topic (str): The name of the topic
    """

    cursor.execute(f"""
        SELECT question, correct_answer, wrong_answer1, wrong answer2, wrong answer_3
        FROM {topic}
        ORDER BY RANDOM()
        LIMIT 5;
    """)
    questions = cursor.fetchall()

    if not questions:
        print(f"No questions found for the '{topic}' topic.")
        return

    score = 0
    # total_questions = len(questions)
    for question, correct, *wrong in questions:
        options = [correct] + [ans for ans in wrong if ans]
        random.shuffle(options)

        print(f"\n{questions}\n")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        try:
            user_answer = int(input("Select the correct answer number:")) - 1
            if 0 <= user_answer < len(options) and options[user_answer] == correct:
                print("Correct!")
                score += 1
            else:
                print(f" ⭕ Wrong! The correct answer is {correct}")
        except ValueError:
            print("�� Invalid selection. Skipping question.")

    print(f"\nQuiz over! Your final score: {score}/{len(questions)}")        


def add_question(cursor, conn):
    """
    Allows the user to add a new question to the database
    to an existing or new topic.

    Args:
        cursor (pg.cursor): Database cursor"
        conn (pg.connection): Database connection"
    """

    topic = input("Enter the topic name: ").lower()

    # Create a table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {topic} (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            wrong_answer1 TEXT NOT NULL,
            wrong_answer2 TEXT NOT NULL,
            wrong_answer_3 TEXT NOT NULL,
        );
    """)
    conn.commit()
    print(f"�� Table '{topic}' created or updated successfully.")

    if conn.notices: #
        print(conn.notices[-1]) #

    question = input("Enter the question: ")
    correct_answer = input("Enter the correct answer: ")
    wrong_answer1 = input("Enter the first wrong answer: ")
    wrong_answer2 = input("Enter the second wrong answer: ")
    wrong_answer3 = input("Enter the third wrong answer: ")

    cursor.execute("""
        INSERT INTO {topic} (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer_3)
        VALUES (%s, %s, %s, %s, %s);
    """, (question, correct, wrong1, wrong2, wrong3 if wrong3 else None)) # create correct, wrong1 ...
    
    conn.commit()
    print("👏🏼 Question added successfully!")


def main():
    """
    The main function to run the quiz application.
    Connects to the database, displays the menu,
    and handles user input to perform actions.
    """

    conn, cursor = connect_db()
    if conn is None:
        return

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            take_quiz(cursor)
        elif choice == "2":
            add_question(cursor, conn)
        elif choice == "3":
            print("🚪 Exiting ... Goodbye!")
            break
        else:
            print("�� Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
import psycopg2 as pg
import random
from config import config
from psycopg2 import sql
import matplotlib.pyplot as plt


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
        conn = pg.connect(**config)
        cursor = conn.cursor()
        print("🗃️ Connected to the PostgreSQL database ✅")
        return conn, cursor
                     
    except (Exception, pg.DatabaseError) as error:
        print("Error while connecting to PostgreSQL ❌", error)
        return None, None


def show_menu():
    """
    Displays the main menu.
    """

    print("\n🎲 Quiz Game")
    print("1. Play a quiz")
    print("2. Show the topics")
    print("3. Add a new question")
    print("4. Delete a topic")
    print("5. Show your score")
    print("6. Show your best scores graph")
    print("7. Exit")


def get_topics(cursor):
    """
    Retrieves a list of available topics from the database.

    Args:
        cursor (pg.cursor): Database cursor

    Returns:
        list: A list of available topic names.
    """

    cursor.execute("SELECT topic_name FROM topics")
    rows = cursor.fetchall()
    # conn.close
    return [row[0] for row in rows]

def show_topics(cursor):
    """
    Shows the available topics from the database.

    Args:
        cursor (pg.cursor): Database cursor
    """

    topics = get_topics(cursor)
    if not topics:
        print("No topics found. Please add some topics first.")
        return

    else:
        print("\nAvailable topics:")
        for idx, topic in enumerate(topics, 1):
            print(f"{idx}. {topic}")


def delete_topic(cursor, conn):
    show_topics(cursor)
    topic = input("Enter the topic name to delete: ").lower()

    cursor.execute("SELECT to_regclass(%s);", (topic,))
    result = cursor.fetchone()

    if result[0] is None:
        print(f"Topic '{topic}' does not exist.")
        return

    cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(topic)))
    conn.commit()
    print(f"Topic '{topic}' deleted successfully.")


def take_quiz(cursor, conn):
    """
    Take a quiz.

    Args:
        cursor (pg.cursor): Database cursor
        conn (pg.connection): Database connection
    """

    # Fetch available topics
    topics = get_topics(cursor)
    if not topics:
        print("No topics found. Please add some topics first.")
        return

    show_topics(cursor)

    try:
        # Get user's topic choice
        choice = int(input("Select a topic number:")) - 1  # number of topics
        if 0 <= choice < len(topics):
            topic = topics[choice]
            start_quiz(cursor, conn, topic)
        else:
            print("😔 Invalid topic number. Please try again.")
    except ValueError:
        print("Invalid selection. Please try again.")


def start_quiz(cursor, conn, topic):
    """
    Fetches random questions from the selected topic, with a chosen
    difficulty level and starts the quiz.

    Args:
        cursor (pg.cursor): Database cursor
        conn (pg.connection): Database connection
        topic (str): The name of the topic
    """
    try:
        # Get difficulty level
        difficulty = int(input("Select difficulty level (1-Easy, 2-Medium, 3-Hard):"))
        if difficulty not in [1, 2, 3]:
            print("Invalid difficulty level. Defaulting to Easy.")
            difficulty = 1
    except ValueError:
        print("Invalid selection. Defaulting to Easy.")
        difficulty = 1

    # Fetch questions from the database for the selected topic and difficulty level
    cursor.execute("""
        SELECT question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3
        FROM questions
        JOIN topics ON topics.id = questions.topic_id
        WHERE topics.topic_name = %s AND questions.difficulty = %s
        ORDER BY RANDOM()
        LIMIT 5;
    """, (topic, difficulty))

    questions = cursor.fetchall()

    if not questions:
        print(f"No questions found for the '{topic}' topic at difficulty level {difficulty}.")
        return

    score = 0
    # Loop through each question, display it and check the user's answer
    for question, correct, *wrong in questions:
        options = [correct] + [ans for ans in wrong if ans]
        random.shuffle(options)

        print(f"\n{question}\n")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        try:
            # Get user answer
            user_answer = int(input("Select the correct answer number:")) - 1
            if 0 <= user_answer < len(options) and options[user_answer] == correct:
                print("Correct!")
                score += 1
            else:
                print(f" ⭕ Wrong! The correct answer is {correct}")
        except ValueError:
            print("Invalid selection. Skipping question.")

    print(f"\nQuiz over! Your final score: {score}/{len(questions)}")

    # Get the user's name and store the score in the database
    username = input("Enter your username: ")

    cursor.execute("INSERT INTO scores (username, score) VALUES (%s, %s);", (username, score))
    conn.commit()

    print("Your score has been recorded successfully!")


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
    cursor.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            wrong_answer1 TEXT NOT NULL,
            wrong_answer2 TEXT NOT NULL,
            wrong_answer3 TEXT NOT NULL,
            difficulty INT CHECK (difficulty BETWEEN 1 AND 3) NOT NULL,
        );
    """).format(sql.Identifier(topic)))
    conn.commit()
    print(f"Table '{topic}' created or updated successfully.")


    question = input("Enter the question: ")
    correct_answer = input("Enter the correct answer: ")
    wrong_answer1 = input("Enter the first wrong answer: ")
    wrong_answer2 = input("Enter the second wrong answer: ")
    wrong_answer3 = input("Enter the third wrong answer: ")
    difficulty = int(input("Enter the difficulty level (1-Easy, 2-Medium, 3-Hard): "))

    cursor.execute(sql.SQL("""
        INSERT INTO {} (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, difficulty)
        VALUES (%s, %s, %s, %s, %s, %s);
    """).format(sql.Identifier(topic)), (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, difficulty))
    
    conn.commit()
    print("👏🏼 Question added successfully!")


def show_score():
    """
    Shows the user's score from the database.
    """

    cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 5;")
    rows = cursor.fetchall()

    if not rows:
        print("No scores found.")
        return

    print("\nTop 5 Scores:")
    for idx, (username, score) in enumerate(rows, 1):
        print(f"{idx}. {username}: {score}")    


def show_best_scores_graph(cursor):
    """
    Shows a graphical representation of the user's best scores.
    """
    cursor.execute("SELECT username, score FROM scores ORDER BY score DESC LIMIT 5;")
    scores = cursor.fetchall()
    
    if not scores:
        print("No scores found.")
        return

    usernames = [user[0] for user in scores]
    top_scores = [user[1] for user in scores]

    plt.bar(usernames, top_scores, color="blue")
    plt.xlabel("Username")
    plt.ylabel("Score")
    plt.title("Top 5 Quiz Scores")
    plt.show()


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
            show_topics(cursor)
        elif choice == "3":
            add_question(cursor, conn)
        elif choice == "4":
            delete_topic(cursor, conn)
        elif choice == "5":
            show_score()
        elif choice == "6":
            show_best_scores_graph(cursor)
        elif choice == "7":
            print("🚪 Exiting ... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

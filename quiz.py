import psycopg2 as pg
import random
from config import config
from psycopg2 import sql
import matplotlib


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
    topic = input("Enter the topic name to delete: ")
    cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(topic)))
    conn.commit()
    print(f"Topic '{topic}' deleted successfully.")



def take_quiz(cursor):
    """
    Take a quiz.

    Args:
        cursor (pg.cursor): Database cursor"
    """

    topics = get_topics(cursor)
    if not topics:
        print("No topics found. Please add some topics first.")
        return
    show_topics(cursor)


    try:
        choice = int(input("Select a topic number:")) - 1  # number of topics
        if 0 <= choice < len(topics):
            topic = topics[choice]
            start_quiz(cursor, topic)
        else:
            print("😔 Invalid topic number. Please try again.")
    except ValueError:
        print("Invalid selection. Please try again.")


def start_quiz(cursor, topic):
    """
    Fetches random questions from the selected topic, with a chosen
    difficulty level and starts the quiz.

    Args:
        cursor (pg.cursor): Database cursor
        topic (str): The name of the topic
    """
    try:
        difficulty = int(input("Select difficulty level (1-Easy, 2-Medium, 3-Hard):"))
        if difficulty not in [1, 2, 3]:
            print("Invalid difficulty level. Defaulting to Easy.")
            difficulty = 1
    except ValueError:
        print("Invalid selection. Defaulting to Easy.")
        difficulty = 1

    cursor.execute(sql.SQL("""
        SELECT question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3
        FROM {}
        ORDER BY RANDOM()
        LIMIT 5;
    """).format(sql.Identifier(topic)))
    questions = cursor.fetchall()

    if not questions:
        print(f"No questions found for the '{topic}' topic ad difficulty level {difficulty}.")
        return

    score = 0
    for question, correct, *wrong in questions:
        options = [correct] + [ans for ans in wrong if ans]
        random.shuffle(options)

        print(f"\n{question}\n")
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
            print("Invalid selection. Skipping question.")

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


def show_best_scores_graph():
    """
    Shows a graphical representation of the user's best scores.

    """
    topics = ["Geography", "Science", "History", "Literature", "Languages"]
    scores = [80, 90, 75, 80, 95]
    plt.bar(topics, scores, color=["blue", "green", "red"])
    plt.xlabel("Topics")
    plt.ylabel("Scores")
    plt.title("Best Quiz Scores by Topics")
    plt.show()


    cursor.execute("SELECT score FROM scores ORDER BY score DESC;")
    scores = [score for _, score in cursor.fetchall()]

    if not scores:
        print("No scores found.")
        return

    print("\nBest Scores Graph:")

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
            show_best_scores_graph()
        elif choice == "7":
            print("🚪 Exiting ... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

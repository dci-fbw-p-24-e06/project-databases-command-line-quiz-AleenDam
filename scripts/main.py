import random
import matplotlib.pyplot as plt
from questions import *  # Import all functions from questions.py

def validate_question_data(question_data):
    """Ensure each question has exactly six elements: one question and five answers."""
    if len(question_data) != 6:
        print(f"❌ Invalid number of elements in question_data: {question_data}")
        return False
    return True

def show_menu():
    """Displays the main menu options."""
    print("\n=== Quiz Application ===")
    print("1. Take a quiz")
    print("2. Add new questions")
    print("3. View all topics")
    print("4. Manage topics")
    print("5. View your scores")
    print("6. Change user")
    print("7. Show all scores")
    print("8. Who is the winner")
    print("9. Exit")


def validate_difficulty():
    """Validates the difficulty level input."""
    difficulty_level = input("Select difficulty level (1 - Easy, 2 - Medium, 3 - Hard): ")
    if difficulty_level not in ["1", "2", "3"]:
        print("❌ Invalid choice. Please choose a difficulty between 1 and 3.")
        return None
    return int(difficulty_level)


def take_quiz(logged_in_user):
    """Function to take the quiz."""
    topics = get_topics()

    if not topics:
        print("❌ No topics available.")
        return

    print("\nAvailable topics:")
    for index, topic in enumerate(topics, 1):
        print(f"{index}. {topic.capitalize()}")

    try:
        topic_choice = int(input("Select a topic (enter number): ")) - 1
        if topic_choice < 0 or topic_choice >= len(topics):
            print("❌ Invalid choice.")
            return
        topic = topics[topic_choice]
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
        return

    difficulty_level = validate_difficulty()
    if not difficulty_level:
        return

    questions = get_questions(topic, difficulty_level)

    if not questions:
        print(f"❌ No questions available for the topic '{topic}' with difficulty level {difficulty_level}.")
        return

    asked_questions = set()
    score = 0
    rounds = 0
    total_rounds = min(10, len(questions))

    random.shuffle(questions)
    index = 0

    while rounds < total_rounds and index < len(questions):
        question = questions[index]
        index += 1

        if question[0] in asked_questions:
            continue

        all_answers = list(filter(None, question[1:7]))

        if len(all_answers) < 2:
            print("⚠️ Skipping malformed question.")
            continue

        print(f"\nRound {rounds + 1}")
        print(f"Question: {question[0]}")
        random.shuffle(all_answers)

        for i, ans in enumerate(all_answers):
            print(f"{i + 1}. {ans}")

        try:
            user_input = input("\nEnter your answer: ").strip()
            answer_index = int(user_input) - 1

            if 0 <= answer_index < len(all_answers):
                if all_answers[answer_index] == question[1]:
                    print("✅ Correct!")
                    score += 1
                else:
                    print(f"❌ Incorrect. The correct answer was: {question[1]}")
            else:
                print("❌ Choice out of range.")
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")

        asked_questions.add(question[0])
        rounds += 1

    print(f"\nYour final score after {rounds} round{'s' if rounds != 1 else ''}: {score}/{rounds}")
    save_score(logged_in_user, topic, score)


def view_topics():
    """Displays all available topics in the database."""
    topics = get_topics()  # Reusing the get_topics function to fetch topics
    if topics:
        print("Available Topics:")
        for idx, topic in enumerate(topics, start=1):
            print(f"{idx}. {topic.capitalize()}")
    else:
        print("❌ No topics found.")

def view_user_scores(logged_in_user):
    """Displays all saved scores and plots a graph for the user's strongest topics."""
    if not logged_in_user:
        print("❌ You need to login first.")
        return

    scores = view_scores(logged_in_user)
    
    if scores:
        print("\n=== User's Average Scores ===")
        for topic, avg_score in scores:
            print(f"Topic: {topic.capitalize()} | Average Score: {avg_score:.2f}")
        
        topics = [score[0] for score in scores]
        avg_scores = [score[1] for score in scores]
        
        plt.figure(figsize=(10, 6))
        plt.barh(topics, avg_scores, color='skyblue')
        plt.xlabel('Average Score')
        plt.title(f"{logged_in_user.capitalize()}'s Strongest Topics")
        plt.show()
    else:
        print(f"No scores found for user '{logged_in_user}'.")

def delete_existing_topic():
    """Deletes an existing topic."""
    topic_name = input("Enter the topic name to delete: ").strip().lower()
    if not topic_name:
        print("❌ Topic name cannot be empty.")
        return

    available_topics = [t.lower() for t in get_topics()]  # normalize for comparison

    if topic_name not in available_topics:
        print("❌ Topic not found.")
        return

    delete_topic(topic_name)
    print(f"✅ Topic '{topic_name}' deleted successfully.")


def display_topics():
    """Displays available topics for the user to choose from."""
    topics = get_topics()
    if not topics:
        print("No topics available!")
        return None
    
    print("Available topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"{idx}. {topic.capitalize()}")

    try:
        topic_number = int(input("Select a topic (enter number): "))
        if topic_number < 1 or topic_number > len(topics):
            print("Invalid choice. Please select a valid number.")
            return None
        return topics[topic_number - 1]
    except ValueError:
        print("Please enter a valid number.")
        return None

def display_questions(topic):
    """Displays questions from the selected topic."""
    try:
        num_questions = int(input("How many questions would you like to answer? "))
        if num_questions <= 0:
            print("Please enter a positive number of questions.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    # Fetch random questions for the selected topic
    questions = get_questions(topic, limit=num_questions)
    
    if not questions:
        print("No questions available for this topic.")
        return

    # Display questions and answers
    for idx, (question, correct_answer, *wrong_answers) in enumerate(questions, start=1):
        print(f"\nQuestion {idx}: {question}")
        choices = [correct_answer] + wrong_answers
        random.shuffle(choices)  # Shuffle answer choices
        for i, choice in enumerate(choices, start=1):
            print(f"{i}. {choice}")

        # Accept answer from the user
        try:
            answer = int(input(f"Your answer (1-{len(choices)}): "))
            if choices[answer - 1] == correct_answer:
                print("Correct!")
            else:
                print(f"Wrong! The correct answer was: {correct_answer}")
        except (ValueError, IndexError):
            print("Invalid answer selection.")    
    
def login():
    """Handles user login."""
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if authenticate_user(username, password):
        print("✅ Login successful!")
        return username
    else:
        print("❌ Invalid username or password.")
        return None
    


def authenticate_user(username, password):
    """Mock function to authenticate a user."""
    # This can be replaced with a database lookup or any other authentication mechanism
    users_db = {
        "aleen": "777",  # Username: Password pair for mock authentication
        "john": "123",
        "julian": "111"
    }
    
    if username in users_db and users_db[username] == password:
        return True
    return False

def show_all_user_scores():
    """Display average scores of all users."""
    all_scores = get_all_user_scores()  # This should return a list of (username, topic, avg_score)
    if not all_scores:
        print("No user scores available.")
        return
    
    print("\n=== All User Scores ===")
    for username, topic, avg in all_scores:
        print(f"{username.capitalize()} | Topic: {topic.capitalize()} | Avg Score: {avg:.2f}")

def show_winner():
    """Display the user with the highest average score."""
    winner_data = get_top_user()
    if winner_data:
        username, avg_score = winner_data
        print(f"🏆 Winner: {username.capitalize()} with an average score of {avg_score:.2f}")
    else:
        print("No scores found to determine a winner.")


def main():
    """Main function for handling user interaction."""
    logged_in_user = None

    # Add hardcoded questions before starting the main loop
    add_hardcoded_questions()

    while logged_in_user is None:
        print("\n=== Welcome to the Quiz Application ===")
        print("1. Login")
        print("2. Register")
        choice = input("Please select an option (1 or 2): ").strip()

        if choice == "1":
            logged_in_user = login()
        elif choice == "2":
            # Register a new user
            username = create_user_account()
            if username:
                print(f"Welcome {username}!")
            else:
                print("Registration failed. Try again.")
        else:
            print("Invalid choice. Please select 1 or 2.")

    while logged_in_user:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            take_quiz(logged_in_user)

        elif choice == "2":
            topics = get_topics()

            print("\nAvailable Topics:")
            if topics:
                for i, t in enumerate(topics, 1):
                    print(f"{i}. {t.replace('_', ' ').title()}")
            else:
                print("⚠️ No topics available yet.")

            choice = input("Do you want to choose from existing topics or create a new one? (choose/create): ").strip().lower()

            if choice == "choose":
                topic_name = input("Enter the topic name for the question: ").strip().lower()

                if topic_name not in [t.lower() for t in topics]:
                    print(f"❌ '{topic_name}' topic does not exist.")
                    continue
            elif choice == "create":
                topic_name = input("Enter the new topic name: ").strip().lower()
                add_topic(topic_name)  # Adds the new topic
            else:
                print("❌ Invalid choice. Please enter 'choose' or 'create'.")
                continue


            difficulty = validate_difficulty()
            if difficulty:
                question = input("Enter the question: ").strip()
                correct_answer = input("Enter correct answer: ").strip()
                
                # Collect 3 wrong answers, and add an empty string if fewer than 4 are provided
                wrong_answers = []
                for i in range(4):
                    wrong_answer = input(f"Enter wrong answer {i + 1}: ").strip()
                    wrong_answers.append(wrong_answer)

                # Append an empty string if only 3 answers are provided
                if len(wrong_answers) < 4:
                    wrong_answers.append('')

                add_question(topic_name, difficulty, question, correct_answer, wrong_answers)

        elif choice == "3":
            view_topics()

        elif choice == "4":
            delete_existing_topic()

        elif choice == "5":
            view_user_scores(logged_in_user)

        elif choice == "6":
            print("🔁 Logging out and switching user...")
            logged_in_user = None
            while logged_in_user is None:
                logged_in_user = login()

        elif choice == "7":
            show_all_user_scores()

        elif choice == "8":

            show_winner()

        elif choice == "9":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()



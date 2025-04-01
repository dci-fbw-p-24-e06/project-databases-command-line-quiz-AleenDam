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
    print("2. Add a new topic")
    print("3. Add a question to an existing topic")
    print("4. View all topics")
    print("5. Delete a topic")
    print("6. View scores")
    print("7. Logout")
    print("8. Exit")

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
        print(f"{index}. {topic}")

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

    score = 0
    asked_questions = set()
    rounds = 0
    total_rounds = 10  # Set the total number of rounds you want

    while rounds < total_rounds:
        # Shuffle questions if necessary to avoid repetition
        random.shuffle(questions)
        
        question = questions[rounds % len(questions)]  # Ensuring it doesn't go out of index range
        if question[0] in asked_questions:
            continue
        
        print(f"\nRound {rounds + 1}:")
        print(f"Question: {question[0]}")
        answers = [question[1], question[2], question[3], question[4], question[5], question[6]]
        random.shuffle(answers)
        print("\n".join(f"{i+1}. {ans}" for i, ans in enumerate(answers)))
        
        try:
            answer = int(input("\nEnter your answer: ")) - 1
            if 0 <= answer < len(answers) and answers[answer] == question[1]:
                score += 1
            else:
                print("❌ Incorrect answer.")
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        
        asked_questions.add(question[0])
        rounds += 1

    print(f"\nYour final score after {total_rounds} rounds: {score}/{total_rounds}")
    save_score(logged_in_user, topic, score)


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
    topic_name = input("Enter the topic name to delete: ").strip()
    if not topic_name:
        print("❌ Topic name cannot be empty.")
        return
    
    if topic_name not in get_topics():
        print("❌ Topic not found.")
        return

    delete_topic(topic_name)
    print(f"✅ Topic '{topic_name}' deleted successfully.")
    
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
        "john": "1234"
    }
    
    if username in users_db and users_db[username] == password:
        return True
    return False

# Your other functions (validate_question_data, show_menu, etc.) remain unchanged.

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
            logged_in_user = create_user_account()
        else:
            print("❌ Invalid option. Please select 1 to login or 2 to register.")

    while logged_in_user:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            take_quiz(logged_in_user)
        elif choice == "2":
            topic_name = input("Enter topic name: ").strip()
            if topic_name:
                add_topic(topic_name)
        elif choice == "3":
            topic = input("Enter topic name: ").strip()
            if topic:
                module = input("Enter module: ").strip()
                submodule = input("Enter submodule: ").strip()
                difficulty = validate_difficulty()
                if difficulty:
                    question = input("Enter the question: ").strip()
                    correct_answer = input("Enter correct answer: ").strip()
                    wrong_answers = [input(f"Enter wrong answer {i+1}: ").strip() for i in range(3)]
                    add_question(topic, module, submodule, difficulty, question, correct_answer, wrong_answers)
        elif choice == "4":
            topics = get_topics()
            if topics:
                print("\nTopics:", ", ".join(topics))
            else:
                print("❌ No topics available.")
        elif choice == "5":
            delete_existing_topic()
        elif choice == "6":
            view_user_scores(logged_in_user)
        elif choice == "7":
            print("Logging out...")
            logged_in_user = None
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()


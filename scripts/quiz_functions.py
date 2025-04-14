import random
import matplotlib.pyplot as plt
from questions import *  # Import all functions from questions.py
from take_quiz import *
from auth import *


def show_menu():
    """Displays the main menu options."""
    print("\n=== Quiz Application ===")
    print("1. Take a quiz")
    print("2. Add new questions")
    print("3. View all topics")
    print("4. Delete topics")
    print("6. Change user")
    print("7. My scores")
    print("8. Show all users scores")
    print("9. Who is the winner")
    print("10. Exit")


def add_new_question():
    """Handles the process of adding a new question to a topic."""
    # Fetch and display all available topics
    topics = get_topics()

    print("\nAvailable topics:")
    for display_name in topics.keys():
        print(f"- {display_name}")

    # Prompt to either add question to an existing topic or create a new one
    choice = input("\nEnter 'choose' to add a question to an existing topic or 'create' to create a new topic: ").strip().lower()

    if choice == "choose":
        # Let the user choose a topic by name (case-insensitive)
        topic_name = input("Enter the name of the topic you want to add a question to: ").strip().lower()

        # Ensure the user selects a valid topic (case-insensitive check)
        valid_topics = {name.lower(): name for name in topics.keys()}
        if topic_name not in valid_topics:
            print(f"❌ '{topic_name}' is not a valid topic.")
            return

        # Get the correct display name for the topic
        selected_topic = valid_topics[topic_name]

        # Collecting other details for the new question
        difficulty = int(input("Enter difficulty (1 - Easy, 2 - Medium, 3 - Hard): ").strip())
        question = input("Enter the question: ").strip()
        correct_answer = input("Enter the correct answer: ").strip()

        # Collect 4 wrong answers
        wrong_answers = []
        for i in range(4):
            wrong_answers.append(input(f"Enter wrong answer {i+1}: ").strip())

        # Call add_questions with the gathered inputs
        add_questions(selected_topic, difficulty, question, correct_answer, wrong_answers)
        print(f"✅ Question added to the topic '{selected_topic}'.")

    elif choice == "create":
        # User wants to create a new topic and add a question
        topic_name = input("Enter the name of the new topic: ").strip()

        # Create the new topic (assuming there's a function to handle this)
        add_topic(topic_name)

        # Now that the topic is created, collect question details
        difficulty = int(input("Enter difficulty (1 - Easy, 2 - Medium, 3 - Hard): ").strip())
        question = input("Enter the question: ").strip()
        correct_answer = input("Enter the correct answer: ").strip()

        # Collect 4 wrong answers
        wrong_answers = []
        for i in range(4):
            wrong_answers.append(input(f"Enter wrong answer {i+1}: ").strip())

        # Call add_questions with the gathered inputs for the new topic
        add_questions(topic_name, difficulty, question, correct_answer, wrong_answers)
        print(f"✅ Question added to the new topic '{topic_name}'.")

    else:
        print("❌ Invalid choice. Please enter 'choose' or 'create'.")



def view_all_topics():
    """Fetch and display all topics from the database in a user-friendly format."""
    topic_mapping = get_topics()

    if not topic_mapping:
        print("No topics available.")
    else:
        print("Available topics:")
        for index, (display_name, raw_name) in enumerate(topic_mapping.items(), 1):
            print(f"{index}. {display_name}")
    
    return topic_mapping  # Return the topics mapping

def delete_topic():
    """Deletes a topic from the database."""
    view_all_topics()  # Show available topics before deletion
    try:
        topic_number = int(input("Select a topic you want to delete (enter number): "))
        topics = get_topics()  # Fetch the topics again to ensure fresh data
        selected_topic = list(topics.keys())[topic_number - 1]

        confirmation = input(f"Are you sure you want to delete the topic '{selected_topic}' with all questions? (y/n): ")
        if confirmation.lower() == 'y':
            delete_topic_from_db(selected_topic)
            print(f"Topic '{selected_topic}' and its associated data have been deleted from the database.")
            
            # Show updated topics after deletion
            updated_topics = get_topics()
            print("\nUpdated list of topics:")
            for idx, (display_name, _) in enumerate(updated_topics.items(), 1):
                print(f"{idx}. {display_name}")
        else:
            print("Topic deletion cancelled.")
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
    except IndexError:
        print("❌ Invalid topic selection. Please choose a valid topic number.")
    except Exception as e:
        print(f"❌ An error occurred while deleting the topic: {str(e)}")



def view_user_scores(logged_in_user):
    """Displays all saved scores and plots a graph for the user's strongest topics."""
    if not logged_in_user:
        print("❌ You need to login first.")
        return

    scores = view_scores(logged_in_user)  # Get scores for the logged-in user
    
    if scores:
        print("\n=== User's Average Scores ===")
        for topic, avg_score in scores:
            print(f"Topic: {topic.capitalize()} | Average Score: {avg_score:.2f}")
        
        # Prepare data for the bar graph
        topics = [score[0] for score in scores]
        avg_scores = [score[1] for score in scores]
        
        # Plot the user's strongest topics (bar graph)
        plt.figure(figsize=(10, 6))
        plt.barh(topics, avg_scores, color='skyblue')
        plt.xlabel('Average Score')
        plt.title(f"{logged_in_user.capitalize()}'s Strongest Topics")
        plt.show()
    else:
        print(f"No scores found for user '{logged_in_user}'.")


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
        """Display the user(s) with the highest average score and most attempts."""
        winners = get_top_user()
        
        # Debugging output
        print(f"Winners fetched: {winners}")

        if winners:
            print("🏆 Winner(s):")
            for winner in winners:
                if len(winner) == 3:  # Ensure correct number of values before unpacking
                    username, avg_score, attempts = winner
                    print(f"{username.capitalize()} - Avg Score: {avg_score:.2f}, Attempts: {attempts}")
                else:
                    print(f"Unexpected result in winner data: {winner}")
        else:
            print("No scores found to determine a winner.")


def show_winner():
    """Displays all winners (users with the highest average score)."""
    winners = get_top_user()

    if not winners:
        print("No scores available to determine a winner.")
    else:
        print("🏆 Top Winner(s):")
        for username, avg_score in winners:
            print(f"{username.capitalize()} with an average score of {avg_score:.2f}")





from collections import defaultdict

def display_questions():
    """Display all questions from a topic selected by the user, grouped by difficulty level."""
    topic_mapping = get_topics()

    if not topic_mapping:
        print("No topics available.")
        return

    # Display available topics
    print("Available topics:")
    for index, (display_name, raw_name) in enumerate(topic_mapping.items(), 1):
        print(f"{index}. {display_name}")

    try:
        topic_choice = int(input("\nEnter the number of the topic you want to view questions from: "))
        if topic_choice < 1 or topic_choice > len(topic_mapping):
            print("Invalid topic selection.")
            return

        selected_topic = list(topic_mapping.values())[topic_choice - 1]

        questions = get_questions(selected_topic)

        if not questions:
            print(f"No questions found for the topic '{selected_topic}'.")
            return

        # Group questions by difficulty using a dictionary
        grouped = defaultdict(list)
        for q in questions:
            grouped[q[-1]].append(q[0])  # q[-1] = difficulty, q[0] = question text

        print(f"\nQuestions from topic: {selected_topic}")
        for difficulty in sorted(grouped.keys()):
            print(f"\n=== Difficulty {difficulty} ===")
            for idx, question_text in enumerate(grouped[difficulty], 1):
                print(f"Q{idx}: {question_text}")
                print("-" * 40)

    except ValueError:
        print("Invalid input. Please enter a valid number.")


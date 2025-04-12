import random
from questions import *

def validate_difficulty():
    """Validates the difficulty level input."""
    difficulty_level = input("Select difficulty level (1 - Easy, 2 - Medium, 3 - Hard): ")
    if difficulty_level not in ["1", "2", "3"]:
        print("❌ Invalid choice. Please choose a difficulty between 1 and 3.")
        return None
    return int(difficulty_level)


def take_quiz(logged_in_user):
    """Function to take the quiz."""
    topic_mapping = get_topics()

    if not topic_mapping:
        print("❌ No topics available.")
        return

    print("\nAvailable topics:")
    for index, (display_name, raw_name) in enumerate(topic_mapping.items(), 1):
        print(f"{index}. {display_name.capitalize()}")

    try:
        topic_choice = int(input("Select a topic (enter number): ").strip()) - 1

        if topic_choice < 0 or topic_choice >= len(topic_mapping):
            print("❌ Invalid choice. Please select a valid topic.")
            return

        topic = list(topic_mapping.values())[topic_choice]
    except ValueError:
        print("❌ Invalid input. Please enter a valid number.")
        return

    difficulty_level = validate_difficulty()  # Using validate_difficulty from quiz_function
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

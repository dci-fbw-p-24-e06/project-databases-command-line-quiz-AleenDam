from auth import login, create_user_account, change_user
from quiz_functions import *

def show_menu():
    """Displays the main menu options."""
    print("\n=== Quiz Application ===")
    print("1. Take a quiz")
    print("2. Add new questions")
    print("3. View all topics")
    print("4. Delete topics")
    print("5. Display questions from a topic")  # New option
    print("6. Change user")
    print("7. My scores")
    print("8. Show all users scores")
    print("9. Who is the winner")
    print("10. Exit")

def main():
    """Main function for handling user interaction."""
    logged_in_user = None

    while logged_in_user is None:
        print("\n=== Welcome to the Quiz Application ===")
        print("1. Login")
        print("2. Register")
        choice = input("Please select an option (1 or 2): ").strip()

        if choice == "1":
            logged_in_user = login()  # This will return the username if successful
        elif choice == "2":
            # Register a new user
            username = create_user_account()  # This will return the username if successful
            if username:
                print(f"Welcome {username}!")
                logged_in_user = username  # Set logged in user to the newly created user
            else:
                print("Registration failed. Try again.")
        else:
            print("Invalid choice. Please select 1 or 2.")

    while logged_in_user:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            take_quiz(logged_in_user)  # Existing quiz logic
        elif choice == "2":
            add_new_question()  # Logic for adding questions
        elif choice == "3":
            view_all_topics()  # Call the function to view topics
        elif choice == "4":
            delete_topic()  # Delete topic logic
        elif choice == "5":
            display_questions()
        elif choice == "6":
            logged_in_user = change_user()  # Logic for changing user
        elif choice == "7":
            view_user_scores(logged_in_user)  # Show scores logic for logged-in user (fixed function name)
        elif choice == "8":
            show_all_user_scores()  # Show all user scores (make sure this function works with or without arguments)
        elif choice == "9":
            show_winner()  # Show winner logic
        elif choice == "10":
            print("Exiting the application...")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()

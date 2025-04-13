import tkinter as tk
from tkinter import messagebox
from auth import login_user, register_user
from questions import add_questions, get_topics, get_questions, get_all_user_scores, get_top_user
import random
from take_quiz import take_quiz
from quiz_functions import *

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Application")
        self.root.geometry("800x800")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.current_user = None  # To track the logged-in user
        self.questions = []  # Initialize an empty list for questions
        self.rounds = 0  # Initialize rounds counter
        self.score = 0  # Initialize score counter

        self.build_login_screen()

    def build_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Login to Quiz", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Username").pack()
        tk.Entry(self.root, textvariable=self.username_var).pack()

        tk.Label(self.root, text="Password").pack()
        tk.Entry(self.root, textvariable=self.password_var, show="*").pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register).pack()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if login_user(username, password):
            self.current_user = username  # Store logged-in user
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.show_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if register_user(username, password):
            messagebox.showinfo("Success", "User registered.")
        else:
            messagebox.showerror("Error", "Could not register user.")

    def show_menu(self):
        """Displays the main menu options."""
        self.clear_screen()

        tk.Label(self.root, text=f"Welcome, {self.current_user}", font=("Helvetica", 16)).pack(pady=20)

        # Ensure consistent use of pack for all buttons
        menu_buttons = [
            ("Take a quiz", self.select_topic),
            ("Add new questions", self.add_new_question),
            ("View all topics", self.view_topics),
            ("Delete topics", self.delete_topics),
            ("Display questions from a topic", self.display_topic_questions),
            ("Change user", self.logout),
            ("My scores", self.view_my_scores),
            ("Show all users' scores", self.view_all_scores),
            ("Who is the winner?", self.view_winner),
            ("Exit", self.root.quit),
        ]
        for text, command in menu_buttons:
            tk.Button(self.root, text=text, command=command).pack(pady=10)

    def select_topic(self):
        self.clear_window()
        tk.Label(self.root, text="Select Topic", font=("Helvetica", 16)).pack(pady=20)

        topics = get_topics()  # Use the correct function name here

        for topic in topics:
            tk.Button(self.root, text=topic, command=lambda t=topic: self.select_difficulty(t)).pack(pady=5)

    def select_difficulty(self, topic):
        self.clear_window()
        tk.Label(self.root, text=f"Select Difficulty for {topic}", font=("Helvetica", 16)).pack(pady=20)

        for level in range(1, 4):
            tk.Button(self.root, text=f"Level {level}", command=lambda l=level: self.start_quiz(topic, l)).pack(pady=5)

    def start_quiz(self, topic, difficulty):
        # Fetch the questions for the selected topic and difficulty
        self.questions = get_questions(topic, difficulty)

        if not self.questions:
            messagebox.showerror("No Questions", f"No questions available for the topic '{topic}' with difficulty {difficulty}.")
            return

        self.rounds = 0  # Reset rounds counter
        self.score = 0  # Reset score
        self.ask_question()  # Start the quiz by asking the first question

    def ask_question(self):
        # Check if we have more questions left to ask
        if self.rounds >= len(self.questions):  # If rounds exceed available questions
            self.end_quiz()  # End the quiz
            return

        question = self.questions[self.rounds]  # Get the current question
        self.current_question = question
        question_text = question[0]  # The question text
        all_answers = list(filter(None, question[1:7]))  # Filter out empty answers
        random.shuffle(all_answers)  # Shuffle answers for random order

        # Display the question and answers in the GUI
        self.clear_window()
        tk.Label(self.root, text=f"Round {self.rounds + 1}: {question_text}", font=("Helvetica", 14)).pack(pady=10)

        for ans in all_answers:
            tk.Button(self.root, text=ans, command=lambda a=ans: self.check_answer(a)).pack(pady=5)

    def check_answer(self, selected_answer):
        correct_answer = self.current_question[1]  # The correct answer is at index 1
        if selected_answer == correct_answer:
            messagebox.showinfo("Correct", "✅ Correct!")
            self.score += 1  # Increment score for correct answer
        else:
            messagebox.showerror("Incorrect", f"❌ Incorrect. The correct answer was: {correct_answer}")

        self.rounds += 1  # Move to the next question
        self.ask_question()  # Ask the next question

    def end_quiz(self):
        # Display the final score at the end of the quiz
        messagebox.showinfo("Quiz Ended", f"Your final score is {self.score}/{self.rounds}.")
        self.clear_window()
        tk.Label(self.root, text="Quiz Over!", font=("Helvetica", 16)).pack(pady=20)
        tk.Button(self.root, text="Return to Main Menu", command=self.show_menu).pack(pady=10)

    def logout(self):
        self.current_user = None
        self.build_login_screen()

    def view_topics(self):
        self.clear_window()
        topics = get_topics()  # Get topics from the database or your source
        tk.Label(self.root, text="Available Topics", font=("Helvetica", 16)).pack(pady=20)

        if not topics:
            # If there are no topics, display a message
            tk.Label(self.root, text="No topics available.", font=("Helvetica", 14)).pack(pady=10)
        else:
            # Display topics as buttons
            for topic in topics:
                tk.Label(self.root, text=topic, font=("Helvetica", 14)).pack(pady=5)

        # Optionally, you can add a button to return to the main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)


    def add_new_question(self):
        """Handles the process of adding a new question to a topic."""
        self.clear_window()
        tk.Label(self.root, text="Add New Question", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        # Fetch existing topics from the database
        topic_mapping = get_topics()  # Returns {"Languages": "languages", ...}
        display_topics = list(topic_mapping.keys())  # For dropdown display

        # Topic selection dropdown
        tk.Label(self.root, text="Select Existing Topic").grid(row=1, column=0, sticky="e")
        selected_topic_display = tk.StringVar()
        if display_topics:
            selected_topic_display.set(display_topics[0])  # Set default topic
        topic_menu = tk.OptionMenu(self.root, selected_topic_display, *display_topics)
        topic_menu.grid(row=1, column=1, sticky="w")

        # OR: Create new topic
        tk.Label(self.root, text="Or Enter New Topic").grid(row=2, column=0, sticky="e")
        new_topic_entry = tk.Entry(self.root)
        new_topic_entry.grid(row=2, column=1, sticky="w")

        # Difficulty
        tk.Label(self.root, text="Difficulty (1-3)").grid(row=3, column=0, sticky="e")
        difficulty_var = tk.IntVar(value=1)
        tk.OptionMenu(self.root, difficulty_var, 1, 2, 3).grid(row=3, column=1, sticky="w")

        # Question and answers
        labels = ["Question", "Correct Answer", "Wrong Answer 1", "Wrong Answer 2", "Wrong Answer 3", "Wrong Answer 4"]
        entries = []
        for idx, label in enumerate(labels, start=4):
            tk.Label(self.root, text=label).grid(row=idx, column=0, sticky="e")
            entry = tk.Entry(self.root)
            entry.grid(row=idx, column=1, sticky="w")
            entries.append(entry)

        # Submit button
        add_button = tk.Button(
            self.root, text="Add Question",
            command=lambda: self.on_add_question(
                topic_mapping, selected_topic_display, new_topic_entry, difficulty_var, *entries
            )
        )
        add_button.grid(row=10, column=0, columnspan=2, pady=10)

    def on_add_question(self, topic_mapping, selected_topic_display, new_topic_entry, difficulty_var, *entries):
        # Unpack entries into individual fields
        question_entry, correct_answer_entry, wrong_answer1_entry, wrong_answer2_entry, wrong_answer3_entry, wrong_answer4_entry = entries

        # Determine which topic to use
        topic_name = new_topic_entry.get().strip() or selected_topic_display.get()
        difficulty = difficulty_var.get()
        question = question_entry.get()
        correct_answer = correct_answer_entry.get()
        wrong_answers = [
            wrong_answer1_entry.get(),
            wrong_answer2_entry.get(),
            wrong_answer3_entry.get(),
            wrong_answer4_entry.get(),
        ]

        # Validate the question data using your existing validation function
        question_data = [question, correct_answer, wrong_answers[0], wrong_answers[1], wrong_answers[2], wrong_answers[3]]
        if not validate_question_data(question_data):
            messagebox.showerror("Error", "Invalid question data. Please check all fields.")
            return

        # Add topic if it's a new one
        if new_topic_entry.get().strip():
            add_topic(new_topic_entry.get().strip())  # Add the new topic and create a table

        # Add question to the correct table using your existing add_questException in Tkinter callback

        add_questions(topic_name, difficulty, question, correct_answer, wrong_answers)
        
        messagebox.showinfo("Success", f"Question added to the topic '{topic_name}'!")

        # Ask if the user wants to continue or return to the main menu
        user_response = messagebox.askyesno("Continue", "Do you want to add another question?")
        if user_response:
            self.add_new_question()  # Continue adding questions
        else:
                self.return_to_main_menu()  # Go back to the main menu


    def delete_topics(self):
        self.clear_window()
        
        topics = get_topics()  # Fetch all topics
        if not topics:
            messagebox.showinfo("No Topics", "There are no topics available to delete.")
            self.show_menu()
            return

        selected_topic = tk.StringVar()
        selected_topic.set(topics[0])

        tk.Label(self.root, text="Select Topic to Delete", font=("Helvetica", 16)).pack(pady=20)
        topic_menu = tk.OptionMenu(self.root, selected_topic, *topics)
        topic_menu.pack(pady=10)

        # Delete button
        tk.Button(self.root, text="Delete Topic", command=lambda: self.confirm_delete_topic(selected_topic.get())).pack(pady=10)

        # Back button
        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)

    def confirm_delete_topic(self, topic_name):
        # Confirm if user really wants to delete the topic
        response = messagebox.askyesno("Delete Topic", f"Are you sure you want to delete the topic '{topic_name}'?")
        if response:
            # Delete the topic using the appropriate backend function
            delete_topic(topic_name)
            messagebox.showinfo("Success", f"Topic '{topic_name}' deleted successfully!")
            self.show_menu()
        else:
            self.show_menu()


    def display_topic_questions(self):
        self.clear_window()

        topics = get_topics()  # Fetch topics
        if not topics:
            messagebox.showinfo("No Topics", "There are no topics available.")
            self.show_menu()
            return

        selected_topic = tk.StringVar()

        # If topics is a dictionary, get the keys (assuming topics are stored as a dictionary)
        if isinstance(topics, dict):
            topics = list(topics.keys())  # Convert dictionary keys to a list of topic names

        # Set the default selected topic if there are topics available
        if topics:
            selected_topic.set(topics[0])

        tk.Label(self.root, text="Select Topic to Display Questions", font=("Helvetica", 16)).pack(pady=20)

        # Create the dropdown menu for selecting a topic
        topic_menu = tk.OptionMenu(self.root, selected_topic, *topics)
        topic_menu.pack(pady=10)

        # Button to show questions for the selected topic
        tk.Button(self.root, text="Show Questions", command=lambda: self.show_questions(selected_topic.get())).pack(pady=10)

        # Back button to return to the main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)



    def show_questions(self, topic_name):
        questions = get_questions(topic_name)  # Fetch the questions for the selected topic

        if not questions:
            messagebox.showinfo("No Questions", f"No questions found for the topic '{topic_name}'.")
            self.show_menu()
            return

        self.clear_window()
        tk.Label(self.root, text=f"Questions for '{topic_name}'", font=("Helvetica", 16)).pack(pady=20)

        # Display questions
        for idx, question in enumerate(questions, start=1):
            tk.Label(self.root, text=f"{idx}. {question[0]}", font=("Helvetica", 14)).pack(pady=5)

        # Back button to return to the main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)


    def view_my_scores(self):
        self.clear_window()
        
        # Fetch the score for the current user
        if not self.current_user:
            messagebox.showerror("Error", "You must be logged in to view scores.")
            self.show_menu()
            return

        scores = view_user_scores(self.current_user)  # Backend function to fetch scores for a user
        if scores is None or len(scores) == 0:
            # If no scores are found, show the "No Scores" message
            #messagebox.showinfo("No Scores", "You have no scores yet.")
            pass
        else:
            # If scores exist, display them
            tk.Label(self.root, text=f"Scores for {self.current_user}", font=("Helvetica", 16)).pack(pady=20)
            for score in scores:
                tk.Label(self.root, text=f"{score[0]}: {score[1]}", font=("Helvetica", 14)).pack(pady=5)

        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)






    def view_all_scores(self):
        self.clear_window()
        
        # Fetch all user scores
        scores = get_all_user_scores()  # Backend function to fetch scores for all users
        if not scores:
            messagebox.showinfo("No Scores", "No scores available.")
        else:
            tk.Label(self.root, text="All Users' Scores", font=("Helvetica", 16)).pack(pady=20)
            for score in scores:
                tk.Label(self.root, text=f"{score[0]}: {score[1]}", font=("Helvetica", 14)).pack(pady=5)

        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)

    def view_winner(self):
        self.clear_window()

        winner = get_top_user()  # Get the user with the highest score
        if not winner:
            messagebox.showinfo("No Winner", "No winner yet.")
        else:
            tk.Label(self.root, text=f"The current winner is: {winner[0]}", font=("Helvetica", 16)).pack(pady=20)

        tk.Button(self.root, text="Back to Main Menu", command=self.show_menu).pack(pady=20)


    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def return_to_main_menu(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to the Quiz App!", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Add New Question", command=self.add_new_question).grid(row=1, column=0, pady=10)
        tk.Button(self.root, text="Other Option 1", command=self.some_other_function).grid(row=2, column=0, pady=10)
        tk.Button(self.root, text="Exit", command=self.root.quit).grid(row=3, column=0, pady=10)    

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

   

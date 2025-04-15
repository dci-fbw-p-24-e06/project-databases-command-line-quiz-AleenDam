import tkinter as tk
from tkinter import messagebox, ttk
import pygame
import os
import tempfile
from PIL import Image, ImageTk
from auth import login_user, register_user
from questions import *
import random
from take_quiz import take_quiz
from quiz_functions import *

class AnimatedQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Application")
        self.root.geometry("1000x800")
        
        # Define color scheme for dark mode
        self.colors = {
            'bg_dark': '#2D1E40',  # Dark purple background
            'bg_medium': '#3D2952',  # Medium purple for frames
            'bg_light': '#4A3163',  # Lighter purple for elements
            'button_primary': '#6A4C93',  # Primary button color
            'button_secondary': '#8A6BBF',  # Secondary button color
            'button_danger': '#A13670',  # Danger/warning button color
            'button_success': '#4A7C59',  # Success button color
            'text': '#FFFFFF',  # White text
            'text_secondary': '#E0E0E0',  # Light gray text
            'highlight': '#1A535C'  # Highlight color (petrol/teal)
        }
        
        # Set the background color of the root window
        self.root.configure(bg=self.colors['bg_dark'])

        # Initialize sounds
        pygame.mixer.init()
        self.sounds = {
            'welcome': pygame.mixer.Sound('sounds/welcome.wav') if os.path.exists('sounds/welcome.wav') else None,
            'correct': pygame.mixer.Sound('sounds/correct.wav') if os.path.exists('sounds/correct.wav') else None,
            'wrong': pygame.mixer.Sound('sounds/wrong.wav') if os.path.exists('sounds/wrong.wav') else None,
            'click': pygame.mixer.Sound('sounds/click.wav') if os.path.exists('sounds/click.wav') else None,
            'complete': pygame.mixer.Sound('sounds/complete.wav') if os.path.exists('sounds/complete.wav') else None
        }

        # Initialize variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.hint_var = tk.StringVar()
        self.current_user = None
        self.questions = []
        self.rounds = 0
        self.score = 0

        # Load images
        self.images = self.load_images()

        # Start with intro screen
        self.show_intro()

    def load_images(self):
        """Load images or create placeholders"""
        image_paths = {
            'welcome': 'images/welcome.png',
            'thinking': 'images/thinking.png',
            'happy': 'images/happy.png',
            'sad': 'images/sad.png'
        }
        images = {}
        for key, path in image_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize((200, 200), Image.LANCZOS)
                    images[key] = ImageTk.PhotoImage(img)
                else:
                    images[key] = self.create_placeholder(key)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                images[key] = self.create_placeholder(key)
        return images

    def create_placeholder(self, image_type):
        """Create placeholder image with text"""
        canvas = tk.Canvas(width=200, height=200, bg=self.colors['highlight'])
        canvas.create_text(100, 100, text=f"Image\n({image_type})", font=("Arial", 14), fill=self.colors['text'])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ps') as ps_file:
            canvas.postscript(file=ps_file.name, colormode='color')
            ps_file.close()
        img = Image.open(ps_file.name)
        img = img.convert('RGB')
        return ImageTk.PhotoImage(img)

    def play_sound(self, sound_name):
        """Play a sound if it exists"""
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")

    def show_intro(self):
        """Display animated intro screen"""
        self.clear_screen()
        self.play_sound('welcome')
        main_frame = tk.Frame(self.root, bg=self.colors['bg_medium'])
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        self.show_intro_content(main_frame)

    def show_intro_content(self, frame):
        """Show the content of the intro screen"""
        title_label = tk.Label(
            frame, 
            text="Welcome to the Quiz Application!", 
            font=("Arial", 28, "bold"), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        )
        title_label.pack(pady=20)

        image_label = tk.Label(frame, image=self.images['welcome'], bg=self.colors['bg_medium'])
        image_label.pack(pady=10)

        message_text = tk.Label(
            frame, 
            text="Let's test your knowledge and have fun together!", 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text'],
            wraplength=500
        )
        message_text.pack(pady=20)

        button_frame = tk.Frame(frame, bg=self.colors['bg_medium'])
        button_frame.pack(pady=20)
        
        start_button = tk.Button(
            button_frame, 
            text="Start Quiz Adventure!", 
            font=("Arial", 14, "bold"), 
            bg=self.colors['button_primary'], 
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'], 
            activeforeground=self.colors['text'],
            width=20, 
            height=2,
            relief=tk.RAISED,
            bd=3,
            command=self.build_login_screen
        )
        start_button.pack(pady=10)

    def pulse_button(self, button, size=1.0, growing=True):
        """Create a pulsing animation for buttons"""
        if not button.winfo_exists():
            return
        if growing:
            size += 0.01
            if size >= 1.1:
                growing = False
        else:
            size -= 0.01
            if size <= 1.0:
                growing = True
                
        try:
            font = button.cget("font")
            font_parts = font.split()
            if len(font_parts) >= 2:
                font_size = int(font_parts[1])
                new_size = int(font_size * size)
                if new_size > 0:  # Ensure font size is positive
                    button.config(font=(font_parts[0], new_size))
        except Exception as e:
            print(f"Error in pulse_button: {e}")
            
        self.root.after(50, lambda: self.pulse_button(button, size, growing))

    def build_login_screen(self):
        """Create an animated login screen"""
        self.clear_screen()
        self.play_sound('click')
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        title_label = tk.Label(
            container, 
            text="Quiz Application", 
            font=("Arial", 28, "bold"), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        )
        title_label.pack(pady=10)

        image_label = tk.Label(container, image=self.images['welcome'], bg=self.colors['bg_medium'])
        image_label.pack(pady=10)

        message_text = tk.Label(
            container, 
            text="Please login to start your quiz adventure!", 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text'], 
            wraplength=500
        )
        message_text.pack(pady=10)

        # Create a nice form with a border
        form_frame = tk.Frame(container, bg=self.colors['bg_light'], bd=2, relief=tk.GROOVE)
        form_frame.pack(pady=20, padx=50)
        
        login_frame = tk.Frame(form_frame, bg=self.colors['bg_light'], padx=30, pady=20)
        login_frame.pack(fill="both", expand=True)

        # Username field
        tk.Label(
            login_frame, 
            text="Username", 
            font=("Arial", 14), 
            bg=self.colors['bg_light'], 
            fg=self.colors['text'],
            anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        username_entry = tk.Entry(
            login_frame, 
            textvariable=self.username_var, 
            font=("Arial", 14), 
            width=30,
            bg="white",
            fg=self.colors['bg_dark'],
            insertbackground=self.colors['bg_dark'],  # Cursor color
            relief=tk.SUNKEN,
            bd=2
        )
        username_entry.pack(pady=(0, 15), fill="x")

        # Password field
        tk.Label(
            login_frame, 
            text="Password", 
            font=("Arial", 14), 
            bg=self.colors['bg_light'], 
            fg=self.colors['text'],
            anchor="w"
        ).pack(fill="x", pady=(5, 2))
        
        password_entry = tk.Entry(
            login_frame, 
            textvariable=self.password_var, 
            show="*", 
            font=("Arial", 14), 
            width=30,
            bg="white",
            fg=self.colors['bg_dark'],
            insertbackground=self.colors['bg_dark'],
            relief=tk.SUNKEN,
            bd=2
        )
        password_entry.pack(pady=(0, 15), fill="x")

        # Password hint field (initially hidden)
        self.hint_label = tk.Label(
            login_frame, 
            text="Password Hint (optional)", 
            font=("Arial", 14), 
            bg=self.colors['bg_light'], 
            fg=self.colors['text'],
            anchor="w"
        )
        
        self.hint_entry = tk.Entry(
            login_frame, 
            textvariable=self.hint_var, 
            font=("Arial", 14), 
            width=30,
            bg="white",
            fg=self.colors['bg_dark'],
            insertbackground=self.colors['bg_dark'],
            relief=tk.SUNKEN,
            bd=2
        )

        buttons_frame = tk.Frame(login_frame, bg=self.colors['bg_light'])
        buttons_frame.pack(pady=10)
        
        login_button = tk.Button(
            buttons_frame, 
            text="Login", 
            command=self.login, 
            font=("Arial", 14, "bold"), 
            bg=self.colors['button_success'], 
            fg=self.colors['text'], 
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            width=15, 
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        
        register_button = tk.Button(
            buttons_frame, 
            text="Register", 
            command=self.register, 
            font=("Arial", 14, "bold"), 
            bg=self.colors['button_primary'], 
            fg=self.colors['text'], 
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            width=15, 
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        
        login_button.pack(side=tk.LEFT, padx=10)
        register_button.pack(side=tk.LEFT, padx=10)

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda event: self.login())

    def login(self):
        self.play_sound('click')
        username = self.username_var.get()
        password = self.password_var.get()
        self.show_animation('thinking', "Let me check your credentials...")
        self.root.after(1500, lambda: self.process_login(username, password))

    def process_login(self, username, password):
        result = login_user(username, password)
        if result:
            self.current_user = username
            self.play_sound('correct')
            self.show_animation('happy', f"Welcome back, {username}! It's great to see you again!")
            self.root.after(2000, self.show_menu)
        else:
            self.play_sound('wrong')
            self.show_animation('sad', "Oops! I couldn't find those credentials. Would you like to see your password hint?")
            self.root.after(2000, lambda: self.ask_for_hint(username))
            
    def ask_for_hint(self, username):
        """Ask if the user wants to see their password hint"""
        response = messagebox.askyesno("Password Hint", "Do you want to see the password hint?", parent=self.root)
        if response:
            self.show_password_hint(username)
        else:
            # If user doesn't want to see the hint, suggest registration
            self.show_animation('sad', "If you don't have an account yet, please register to start your quiz adventure!")
            self.root.after(2000, self.build_login_screen)

    def show_animation(self, emotion, message):
        """Show animation with a message"""
        self.clear_screen()
        frame = tk.Frame(self.root, bg=self.colors['bg_medium'])
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        # Title
        title_label = tk.Label(
            frame, 
            text="Quiz Application", 
            font=("Arial", 28, "bold"), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        )
        title_label.pack(pady=10)

        image_label = tk.Label(frame, image=self.images[emotion], bg=self.colors['bg_medium'])
        image_label.pack(pady=10)

        message_text = tk.Label(
            frame, 
            text=message, 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text'], 
            wraplength=500
        )
        message_text.pack(pady=20)

    def clear_screen(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def register(self):
        self.play_sound('click')
        username = self.username_var.get()
        password = self.password_var.get()
        hint = self.hint_var.get()

        if not hint:
            hint_response = messagebox.askyesno("Password Hint", "Would you like to set a password hint?", parent=self.root)
            if hint_response:
                self.hint_label.pack()
                self.hint_entry.pack()
                messagebox.showinfo("Password Hint", "Please enter a hint for your password.", parent=self.root)
                return
            else:
                hint = ""

        self.show_animation('thinking', "Creating your new account...")
        self.root.after(1500, lambda: self.process_registration(username, password, hint))

    def process_registration(self, username, password, hint):
        if register_user(username, password, hint):
            self.current_user = username
            self.play_sound('correct')
            self.show_animation('happy', f"Welcome, {username}! Your account has been created successfully!")
            self.root.after(2000, self.show_menu)
        else:
            self.play_sound('wrong')
            self.show_animation('sad', "I couldn't register your account. The username might already be taken.")
            self.root.after(2000, self.build_login_screen)

    def show_menu(self):
        """Displays the main menu options with animations."""
        self.clear_screen()
        self.play_sound('click')

        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

        header_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        header_frame.pack(fill="x", pady=10)

        image_label = tk.Label(header_frame, image=self.images['happy'], bg=self.colors['bg_medium'])
        image_label.pack(side=tk.LEFT, padx=20)

        text_frame = tk.Frame(header_frame, bg=self.colors['bg_medium'])
        text_frame.pack(side=tk.LEFT, padx=20, fill="both", expand=True)

        tk.Label(
            text_frame, 
            text=f"Welcome, {self.current_user}!", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        ).pack(anchor="w")
        
        tk.Label(
            text_frame, 
            text="What would you like to do today?", 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        ).pack(anchor="w")

        menu_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        menu_frame.pack(pady=20, fill="both", expand=True)

        menu_frame.columnconfigure(0, weight=1)
        menu_frame.columnconfigure(1, weight=1)

        # Define menu options with consistent colors from our theme
        menu_buttons = [
            ("Take a quiz", self.select_topic, self.colors['button_primary']),
            ("Add new questions", self.add_new_question, self.colors['button_primary']),
            ("View all topics", self.view_topics, self.colors['button_primary']),
            ("Delete topics", self.delete_topics, self.colors['button_danger']),
            ("Display topic questions", self.display_topic_questions, self.colors['button_primary']),
            ("Change user", self.logout, self.colors['button_secondary']),
            ("My scores", self.view_my_scores, self.colors['button_primary']),
            ("Show all users' scores", self.view_all_scores, self.colors['button_primary']),
            ("Who is the winner?", self.view_winner, self.colors['highlight']),
            ("Exit", self.root.quit, self.colors['button_danger']),
        ]

        # Create all buttons at once instead of using animation
        for index, (text, command, color) in enumerate(menu_buttons):
            row, col = divmod(index, 2)
            button = tk.Button(
                menu_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                bg=color,
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=20,
                height=2,
                relief=tk.RAISED,
                bd=3
            )
            button.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

    # Implemented menu action methods
    def select_topic(self):
        """Allows the user to select a topic and take a quiz"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="Select a Topic", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        topic_mapping = get_topics()
        if not topic_mapping:
            self.show_animation('sad', "No topics available. Please add some topics first!")
            self.root.after(2000, self.show_menu)
            return
        
        topics_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        topics_frame.pack(pady=20, fill="both", expand=True)
        
        for i, (display_name, raw_name) in enumerate(topic_mapping.items()):
            topic_button = tk.Button(
                topics_frame,
                text=display_name,
                font=("Arial", 14),
                bg=self.colors['button_primary'],
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=20,
                command=lambda t=raw_name, d=display_name: self.select_difficulty(t, d)
            )
            topic_button.pack(pady=10)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def select_difficulty(self, topic, display_name):
        """Allows the user to select a difficulty level for the quiz"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text=f"Select Difficulty for {display_name}", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        difficulty_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        difficulty_frame.pack(pady=20, fill="both", expand=True)
        
        difficulties = [
            ("Easy", 1, self.colors['button_success']),
            ("Medium", 2, self.colors['button_primary']),
            ("Hard", 3, self.colors['button_danger'])
        ]
        
        for text, level, color in difficulties:
            diff_button = tk.Button(
                difficulty_frame,
                text=text,
                font=("Arial", 14),
                bg=color,
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=20,
                command=lambda t=topic, l=level: self.start_quiz(t, l)
            )
            diff_button.pack(pady=10)
        
        back_button = tk.Button(
            container,
            text="Back to Topics",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.select_topic
        )
        back_button.pack(pady=20)

    def start_quiz(self, topic, difficulty):
        """Starts the quiz with the selected topic and difficulty"""
        self.play_sound('click')
        self.clear_screen()
        
        # Get questions for the selected topic and difficulty
        questions = get_questions(topic, difficulty)
        
        if not questions:
            self.show_animation('sad', f"No questions available for this topic with difficulty level {difficulty}.")
            self.root.after(2000, lambda: self.select_difficulty(topic, topic.capitalize()))
            return
        
        # Shuffle and limit questions
        random.shuffle(questions)
        self.questions = questions[:7]  # Limit to 7 questions
        self.rounds = 0
        self.score = 0
        
        # Start the quiz
        self.show_question()

    def show_question(self):
        """Displays a question and answer choices"""
        if self.rounds >= len(self.questions) or self.rounds >= 7:
            # Quiz is complete
            percentage_score = (self.score / self.rounds) * 100 if self.rounds > 0 else 0
            self.play_sound('complete')
            self.show_animation('happy', f"Quiz complete! Your score: {self.score}/{self.rounds} ({percentage_score:.2f}%)")
            
            # Save the score - get the topic from the database name
            topic_name = self.questions[0][6]  # This should be the topic name
            save_score(self.current_user, topic_name, percentage_score)
            
            self.root.after(3000, self.show_menu)
            return
        
        self.clear_screen()
        question_data = self.questions[self.rounds]
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Display round number and question
        tk.Label(
            container, 
            text=f"Round {self.rounds + 1}/{min(7, len(self.questions))}", 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        question_frame = tk.Frame(container, bg="white", bd=2, relief=tk.RAISED)
        question_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            question_frame, 
            text=question_data[0], 
            font=("Arial", 14), 
            bg="white", 
            fg=self.colors['bg_dark'],
            wraplength=500, 
            justify="left"
        ).pack(pady=10, padx=10)
        
        # Prepare answers
        all_answers = [answer for answer in question_data[1:6] if answer]
        random.shuffle(all_answers)
        
        answers_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        answers_frame.pack(pady=20, fill="both", expand=True)
        
        for i, answer in enumerate(all_answers):
            answer_button = tk.Button(
                answers_frame,
                text=answer,
                font=("Arial", 12),
                bg="white",
                fg=self.colors['bg_dark'],
                activebackground=self.colors['bg_light'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                wraplength=400,
                justify="left",
                relief=tk.RAISED,
                bd=2,
                command=lambda a=answer: self.check_answer(a, question_data[1])
            )
            answer_button.pack(pady=5, fill="x")

    def check_answer(self, selected_answer, correct_answer):
        """Checks if the selected answer is correct"""
        self.clear_screen()
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Create a very compact feedback box
        feedback_frame = tk.Frame(container, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        feedback_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.2)
        
        if selected_answer == correct_answer:
            # Play the correct sound
            try:
                self.play_sound('correct')
            except Exception as e:
                print(f"Error playing correct sound: {e}")
                
            self.score += 1
            
            tk.Label(
                feedback_frame,
                text="✓ Correct!",
                font=("Arial", 16, "bold"),
                bg=self.colors['bg_light'],
                fg=self.colors['button_success']
            ).pack(pady=(15, 5), fill="x")
            
        else:
            # Play the wrong sound
            try:
                self.play_sound('wrong')
            except Exception as e:
                print(f"Error playing wrong sound: {e}")
            
            tk.Label(
                feedback_frame,
                text="✗ Incorrect",
                font=("Arial", 16, "bold"),
                bg=self.colors['bg_light'],
                fg=self.colors['button_danger']
            ).pack(pady=(10, 0), fill="x")
            
            tk.Label(
                feedback_frame,
                text=correct_answer,
                font=("Arial", 12),
                bg=self.colors['bg_light'],
                fg=self.colors['button_success'],
                wraplength=300
            ).pack(pady=(0, 5), fill="x")
        
        self.rounds += 1
        self.root.after(1000, self.show_question)

    def add_new_question(self):
        """Interface for adding a new question to a topic"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text="Add New Question", font=("Arial", 24, "bold"), bg="#FFF8DC").pack(pady=10)
        
        # First step: Choose existing topic or create new one
        choice_frame = tk.Frame(container, bg="#FFF8DC")
        choice_frame.pack(pady=20, fill="x")
        
        choose_button = tk.Button(
            choice_frame,
            text="Choose Existing Topic",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.choose_topic_for_question()
        )
        choose_button.pack(side=tk.LEFT, padx=10, expand=True)
        
        create_button = tk.Button(
            choice_frame,
            text="Create New Topic",
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.create_topic_for_question()
        )
        create_button.pack(side=tk.LEFT, padx=10, expand=True)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def choose_topic_for_question(self):
        """Allows the user to choose an existing topic for a new question"""
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text="Choose a Topic", font=("Arial", 24, "bold"), bg="#FFF8DC").pack(pady=10)
        
        topics_frame = tk.Frame(container, bg="#FFF8DC")
        topics_frame.pack(pady=20, fill="both", expand=True)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            self.show_animation('sad', "No topics available. Please create a new topic first!")
            self.root.after(2000, lambda: self.create_topic_for_question())
            return
        
        # Create a scrollable frame for topics
        canvas = tk.Canvas(topics_frame, bg="#FFF8DC")
        scrollbar = tk.Scrollbar(topics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFF8DC")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for display_name, raw_name in topic_mapping.items():
            topic_button = tk.Button(
                scrollable_frame,
                text=display_name,
                font=("Arial", 12),
                bg="#E0E0E0",
                padx=10,
                pady=5,
                width=30,
                command=lambda t=raw_name, d=display_name: self.question_form(t, d)
            )
            topic_button.pack(pady=5)
        
        back_button = tk.Button(
            container,
            text="Back",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=self.add_new_question
        )
        back_button.pack(pady=10)

    def create_topic_for_question(self):
        """Interface for creating a new topic"""
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text="Create New Topic", font=("Arial", 24, "bold"), bg="#FFF8DC").pack(pady=20)
        
        form_frame = tk.Frame(container, bg="#FFF8DC")
        form_frame.pack(pady=20, fill="x")
        
        tk.Label(form_frame, text="Topic Name:", font=("Arial", 14), bg="#FFF8DC").pack(anchor="w", padx=20)
        
        topic_var = tk.StringVar()
        topic_entry = tk.Entry(form_frame, textvariable=topic_var, font=("Arial", 12), width=40)
        topic_entry.pack(pady=10, padx=20, fill="x")
        
        button_frame = tk.Frame(container, bg="#FFF8DC")
        button_frame.pack(pady=20)
        
        create_button = tk.Button(
            button_frame,
            text="Create Topic",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.process_new_topic(topic_var.get())
        )
        create_button.pack(side=tk.LEFT, padx=10)
        
        back_button = tk.Button(
            button_frame,
            text="Back",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=self.add_new_question
        )
        back_button.pack(side=tk.LEFT, padx=10)

    def process_new_topic(self, topic_name):
        """Processes the creation of a new topic"""
        if not topic_name.strip():
            messagebox.showerror("Error", "Topic name cannot be empty!")
            return
        
        # Add the topic to the database
        add_topic(topic_name)
        
        # Show success message and proceed to question form
        self.show_animation('happy', f"Topic '{topic_name}' created successfully!")
        self.root.after(1500, lambda: self.question_form(topic_name.strip().lower().replace(" ", "_"), topic_name))

    def question_form(self, topic_raw, topic_display):
        """Form for adding a new question to a topic"""
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text=f"Add Question to {topic_display}", font=("Arial", 20, "bold"), bg="#FFF8DC").pack(pady=10)
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(container, bg="#FFF8DC")
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg="#FFF8DC")
        
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Difficulty selection
        tk.Label(form_frame, text="Difficulty:", font=("Arial", 14), bg="#FFF8DC").pack(anchor="w", padx=20, pady=(10, 5))
        
        difficulty_var = tk.IntVar(value=1)
        difficulty_frame = tk.Frame(form_frame, bg="#FFF8DC")
        difficulty_frame.pack(fill="x", padx=20, pady=5)
        
        difficulties = [("Easy", 1), ("Medium", 2), ("Hard", 3)]
        for text, value in difficulties:
            tk.Radiobutton(
                difficulty_frame,
                text=text,
                variable=difficulty_var,
                value=value,
                font=("Arial", 12),
                bg="#FFF8DC"
            ).pack(side=tk.LEFT, padx=10)
        
        # Question text
        tk.Label(form_frame, text="Question:", font=("Arial", 14), bg="#FFF8DC").pack(anchor="w", padx=20, pady=(10, 5))
        
        question_var = tk.StringVar()
        question_entry = tk.Entry(form_frame, textvariable=question_var, font=("Arial", 12), width=50)
        question_entry.pack(padx=20, pady=5, fill="x")
        
        # Correct answer
        tk.Label(form_frame, text="Correct Answer:", font=("Arial", 14), bg="#FFF8DC").pack(anchor="w", padx=20, pady=(10, 5))
        
        correct_var = tk.StringVar()
        correct_entry = tk.Entry(form_frame, textvariable=correct_var, font=("Arial", 12), width=50)
        correct_entry.pack(padx=20, pady=5, fill="x")
        
        # Wrong answers
        wrong_vars = []
        for i in range(4):
            tk.Label(form_frame, text=f"Wrong Answer {i+1}:", font=("Arial", 14), bg="#FFF8DC").pack(anchor="w", padx=20, pady=(10, 5))
            
            wrong_var = tk.StringVar()
            wrong_entry = tk.Entry(form_frame, textvariable=wrong_var, font=("Arial", 12), width=50)
            wrong_entry.pack(padx=20, pady=5, fill="x")
            wrong_vars.append(wrong_var)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="#FFF8DC")
        button_frame.pack(pady=20)
        
        submit_button = tk.Button(
            button_frame,
            text="Submit Question",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.submit_question(
                topic_raw,
                difficulty_var.get(),
                question_var.get(),
                correct_var.get(),
                [var.get() for var in wrong_vars]
            )
        )
        submit_button.pack(side=tk.LEFT, padx=10)
        
        back_button = tk.Button(
            button_frame,
            text="Back",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=lambda: self.choose_topic_for_question()
        )
        back_button.pack(side=tk.LEFT, padx=10)

    def submit_question(self, topic, difficulty, question, correct_answer, wrong_answers):
        """Submits a new question to the database"""
        # Validate inputs
        if not question or not correct_answer or not all(wrong_answers[:2]):
            messagebox.showerror("Error", "Question, correct answer, and at least 2 wrong answers are required!")
            return
        
        # Add the question to the database
        add_questions(topic, difficulty, question, correct_answer, wrong_answers)
        
        # Show success message and return to menu
        self.show_animation('happy', "Question added successfully!")
        self.root.after(1500, self.show_menu)

    def view_topics(self):
        """Displays all available topics"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text="Available Topics", font=("Arial", 24, "bold"), bg="#FFF8DC").pack(pady=20)
        
        topics_frame = tk.Frame(container, bg="#FFFFFF", bd=2, relief=tk.RAISED)
        topics_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            tk.Label(topics_frame, text="No topics available.", font=("Arial", 16), bg="#FFFFFF").pack(pady=20)
        else:
            for i, display_name in enumerate(topic_mapping.keys(), 1):
                tk.Label(
                    topics_frame,
                    text=f"{i}. {display_name}",
                    font=("Arial", 16),
                    bg="#FFFFFF",
                    anchor="w"
                ).pack(pady=10, padx=20, fill="x")
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def delete_topics(self):
        """Interface for deleting topics"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg="#FFF8DC")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(container, text="Delete Topics", font=("Arial", 24, "bold"), bg="#FFF8DC").pack(pady=20)
        
        topics_frame = tk.Frame(container, bg="#FFFFFF", bd=2, relief=tk.RAISED)
        topics_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            tk.Label(topics_frame, text="No topics available to delete.", font=("Arial", 16), bg="#FFFFFF").pack(pady=20)
        else:
            for display_name, raw_name in topic_mapping.items():
                topic_frame = tk.Frame(topics_frame, bg="#FFFFFF")
                topic_frame.pack(pady=5, padx=10, fill="x")
                
                tk.Label(
                    topic_frame,
                    text=display_name,
                    font=("Arial", 14),
                    bg="#FFFFFF",
                    anchor="w"
                ).pack(side=tk.LEFT, padx=10)
                
                delete_button = tk.Button(
                    topic_frame,
                    text="Delete",
                    font=("Arial", 12),
                    bg="#F44336",
                    fg="white",
                    command=lambda t=display_name: self.confirm_delete_topic(t)
                )
                delete_button.pack(side=tk.RIGHT, padx=10)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg="#FF6347",
            fg="white",
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def confirm_delete_topic(self, topic_name):
        """Confirms deletion of a topic"""
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the topic '{topic_name}' with all its questions?\nThis action cannot be undone!",
            parent=self.root
        )
        
        if confirm:
            delete_topic_from_db(topic_name)
            self.show_animation('happy', f"Topic '{topic_name}' has been deleted.")
            self.root.after(1500, self.delete_topics)

    def display_topic_questions(self):
        """Displays all questions for a selected topic"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="View Topic Questions", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            self.show_animation('sad', "No topics available.")
            self.root.after(1500, self.show_menu)
            return
        
        topics_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        topics_frame.pack(pady=20, fill="both", expand=True)
        
        for display_name, raw_name in topic_mapping.items():
            topic_button = tk.Button(
                topics_frame,
                text=display_name,
                font=("Arial", 14),
                bg=self.colors['button_primary'],
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=20,
                command=lambda t=raw_name, d=display_name: self.show_topic_questions(t, d)
            )
            topic_button.pack(pady=10)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def show_topic_questions(self, topic, display_name):
        """Shows all questions for a specific topic"""
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text=f"Questions for {display_name}", 
            font=("Arial", 20, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Create a canvas with scrollbar for the questions
        canvas = tk.Canvas(container, bg=self.colors['bg_medium'])
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        questions_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        questions_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=questions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Get questions for the topic
        questions = get_questions(topic)
        
        if not questions:
            tk.Label(
                questions_frame, 
                text="No questions available for this topic.", 
                font=("Arial", 16), 
                bg=self.colors['bg_medium'],
                fg=self.colors['text']
            ).pack(pady=20)
        else:
            # Group questions by difficulty
            difficulty_groups = {}
            for q in questions:
                difficulty = q[6]  # Difficulty is at index 6
                if difficulty not in difficulty_groups:
                    difficulty_groups[difficulty] = []
                difficulty_groups[difficulty].append(q)
            
            # Display questions by difficulty
            for difficulty in sorted(difficulty_groups.keys()):
                difficulty_label = tk.Label(
                    questions_frame,
                    text=f"Difficulty {difficulty}",
                    font=("Arial", 16, "bold"),
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text']
                )
                difficulty_label.pack(pady=(20, 10), anchor="w")
                
                for i, q in enumerate(difficulty_groups[difficulty], 1):
                    question_frame = tk.Frame(questions_frame, bg="white", bd=1, relief=tk.RAISED)
                    question_frame.pack(pady=5, padx=10, fill="x")
                    
                    tk.Label(
                        question_frame,
                        text=f"Q{i}: {q[0]}",
                        font=("Arial", 14),
                        bg="white",
                        fg=self.colors['bg_dark'],
                        wraplength=600,
                        justify="left",
                        anchor="w"
                    ).pack(pady=5, padx=10, fill="x")
                    
                    tk.Label(
                        question_frame,
                        text=f"Correct Answer: {q[1]}",
                        font=("Arial", 12),
                        bg="white",
                        fg=self.colors['button_success'],
                        wraplength=600,
                        justify="left",
                        anchor="w"
                    ).pack(pady=2, padx=10, fill="x")
                    
                    wrong_answers = [ans for ans in q[2:6] if ans]
                    for j, ans in enumerate(wrong_answers, 1):
                        tk.Label(
                            question_frame,
                            text=f"Wrong Answer {j}: {ans}",
                            font=("Arial", 12),
                            bg="white",
                            fg=self.colors['button_danger'],
                            wraplength=600,
                            justify="left",
                            anchor="w"
                        ).pack(pady=2, padx=10, fill="x")
        
        # Create a button frame to hold both buttons
        button_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        button_frame.pack(pady=10)
        
        # Button to go back to topics list
        topics_button = tk.Button(
            button_frame,
            text="Back to Topics",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.display_topic_questions
        )
        topics_button.pack(side=tk.LEFT, padx=10)
        
        # Button to go back to main menu
        menu_button = tk.Button(
            button_frame,
            text="Back to Main Menu",
            font=("Arial", 12),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        menu_button.pack(side=tk.LEFT, padx=10)

    def logout(self):
        """Logs out the current user and returns to the login screen"""
        self.play_sound('click')
        self.current_user = None
        self.username_var.set("")
        self.password_var.set("")
        self.hint_var.set("")
        self.show_animation('happy', "You have been logged out successfully!")
        self.root.after(1500, self.build_login_screen)

    def view_my_scores(self):
        """Displays the current user's scores"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text=f"{self.current_user}'s Scores", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        scores_frame = tk.Frame(container, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        scores_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Get user's scores
        scores = view_scores(self.current_user)
        
        if not scores:
            tk.Label(
                scores_frame, 
                text="No scores available. Take a quiz first!", 
                font=("Arial", 16), 
                bg=self.colors['bg_light'],
                fg=self.colors['text']
            ).pack(pady=20)
        else:
            # Create headers
            headers_frame = tk.Frame(scores_frame, bg=self.colors['highlight'])
            headers_frame.pack(fill="x")
            
            tk.Label(
                headers_frame, 
                text="Topic", 
                font=("Arial", 14, "bold"), 
                bg=self.colors['highlight'], 
                fg=self.colors['text'], 
                width=20
            ).pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Label(
                headers_frame, 
                text="Average Score", 
                font=("Arial", 14, "bold"), 
                bg=self.colors['highlight'], 
                fg=self.colors['text'], 
                width=15
            ).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Add scores
            for topic, avg_score in scores:
                score_frame = tk.Frame(scores_frame, bg=self.colors['bg_light'])
                score_frame.pack(fill="x")
                
                tk.Label(
                    score_frame, 
                    text=topic.capitalize(), 
                    font=("Arial", 14), 
                    bg=self.colors['bg_light'], 
                    fg=self.colors['text'], 
                    width=20
                ).pack(side=tk.LEFT, padx=5, pady=5)
                
                tk.Label(
                    score_frame, 
                    text=f"{avg_score:.2f}%", 
                    font=("Arial", 14), 
                    bg=self.colors['bg_light'], 
                    fg=self.colors['text'], 
                    width=15
                ).pack(side=tk.LEFT, padx=5, pady=5)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def view_all_scores(self):
        """Displays scores for all users"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="All Users' Scores", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        # Create a canvas with scrollbar for the scores
        canvas = tk.Canvas(container, bg=self.colors['bg_medium'])
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scores_frame = tk.Frame(canvas, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        
        scores_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scores_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Get all user scores
        all_scores = get_all_user_scores()
        
        if not all_scores:
            tk.Label(
                scores_frame, 
                text="No scores available.", 
                font=("Arial", 16), 
                bg=self.colors['bg_light'],
                fg=self.colors['text']
            ).pack(pady=20)
        else:
            # Create headers
            headers_frame = tk.Frame(scores_frame, bg=self.colors['highlight'])
            headers_frame.pack(fill="x")
            
            tk.Label(
                headers_frame, 
                text="Username", 
                font=("Arial", 14, "bold"), 
                bg=self.colors['highlight'], 
                fg=self.colors['text'], 
                width=15
            ).pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Label(
                headers_frame, 
                text="Topic", 
                font=("Arial", 14, "bold"), 
                bg=self.colors['highlight'], 
                fg=self.colors['text'], 
                width=15
            ).pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Label(
                headers_frame, 
                text="Average Score", 
                font=("Arial", 14, "bold"), 
                bg=self.colors['highlight'], 
                fg=self.colors['text'], 
                width=15
            ).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Add scores
            for username, topic, avg_score in all_scores:
                score_frame = tk.Frame(scores_frame, bg=self.colors['bg_light'])
                score_frame.pack(fill="x")
                
                tk.Label(
                    score_frame, 
                    text=username.capitalize(), 
                    font=("Arial", 14), 
                    bg=self.colors['bg_light'], 
                    fg=self.colors['text'], 
                    width=15
                ).pack(side=tk.LEFT, padx=5, pady=5)
                
                tk.Label(
                    score_frame, 
                    text=topic.capitalize(), 
                    font=("Arial", 14), 
                    bg=self.colors['bg_light'], 
                    fg=self.colors['text'], 
                    width=15
                ).pack(side=tk.LEFT, padx=5, pady=5)
                
                tk.Label(
                    score_frame, 
                    text=f"{float(avg_score):.2f}%", 
                    font=("Arial", 14), 
                    bg=self.colors['bg_light'], 
                    fg=self.colors['text'], 
                    width=15
                ).pack(side=tk.LEFT, padx=5, pady=5)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        back_button.pack(pady=10)

    def view_winner(self):
        """Displays the user(s) with the highest average score"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="🏆 Top Winner(s) 🏆", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        winners_frame = tk.Frame(container, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        winners_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Get winners
        winners = get_top_user()
        
        if not winners:
            tk.Label(
                winners_frame, 
                text="No scores available to determine a winner.", 
                font=("Arial", 16), 
                bg=self.colors['bg_light'],
                fg=self.colors['text']
            ).pack(pady=20)
        else:
            for i, (username, avg_score) in enumerate(winners, 1):
                winner_frame = tk.Frame(winners_frame, bg=self.colors['highlight'])
                winner_frame.pack(pady=10, padx=10, fill="x")
                
                tk.Label(
                    winner_frame,
                    text=f"{i}. {username.capitalize()}",
                    font=("Arial", 18, "bold"),
                    bg=self.colors['highlight'],
                    fg=self.colors['text']
                ).pack(pady=5)
                
                tk.Label(
                    winner_frame,
                    text=f"Average Score: {float(avg_score):.2f}%",
                    font=("Arial", 16),
                    bg=self.colors['highlight'],
                    fg=self.colors['text']
                ).pack(pady=5)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def show_password_hint(self, username):
        """Shows the password hint for a user"""
        from db import connect_db
        conn = connect_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT hint FROM users WHERE username = %s", (username,))
            hint_result = cursor.fetchone()
        conn.close()
        
        # Create a custom hint dialog instead of using messagebox
        self.clear_screen()
        hint_frame = tk.Frame(self.root, bg=self.colors['bg_medium'])
        hint_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.4)
        
        tk.Label(
            hint_frame, 
            text="Password Hint", 
            font=("Arial", 20, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=(20, 10))
        
        hint_box = tk.Frame(hint_frame, bg=self.colors['highlight'], bd=2, relief=tk.RAISED)
        hint_box.pack(pady=10, padx=20, fill="both", expand=True)
        
        if hint_result and hint_result[0]:
            hint = hint_result[0]
            hint_text = f"Hint: {hint}"
        else:
            hint_text = "No hint available for this user."
            
        tk.Label(
            hint_box, 
            text=hint_text, 
            font=("Arial", 14), 
            bg=self.colors['highlight'],
            fg=self.colors['text'],
            wraplength=400
        ).pack(pady=20, padx=20)
        
        ok_button = tk.Button(
            hint_frame,
            text="OK",
            font=("Arial", 12, "bold"),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            command=self.build_login_screen,
            width=10
        )
        ok_button.pack(pady=20)
        
        # Center the button
        ok_button.update_idletasks()
        button_width = ok_button.winfo_width()
        hint_frame_width = hint_frame.winfo_width()
        ok_button.place(relx=0.5, rely=0.85, anchor="center")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimatedQuizApp(root)
    root.mainloop()
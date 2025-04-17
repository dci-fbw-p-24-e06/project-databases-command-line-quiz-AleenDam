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
                    # Use different sizes for different images
                    if key == 'welcome':
                        # Keep the welcome image larger
                        img = img.resize((800, 600), Image.LANCZOS)
                    else:
                        # Other images remain at 200x200
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

    def create_binary_rain_canvas(self, parent, width, height):
        """Create a canvas with animated binary rain effect"""
        # Use fixed dimensions if width/height are not properly initialized
        if width < 100:
            width = 800
        if height < 100:
            height = 600
            
        canvas = tk.Canvas(parent, width=width, height=height, bg=self.colors['bg_dark'], highlightthickness=0)
        
        # Spring green color for the binary digits
        spring_green = "#4CAF50"
        light_green = "#8BC34A"
        
        # Create binary digits (0s and 1s) - use fewer digits for better performance
        self.rain_digits = []
        for _ in range(50):  # Reduced number of falling digits
            x = random.randint(0, width)
            y = random.randint(-height, 0)  # Start above the canvas
            digit = random.choice(["0", "1"])
            color = random.choice([spring_green, light_green])
            size = random.randint(10, 18)
            speed = random.uniform(1, 3)  # Slightly slower for better performance
            
            text_id = canvas.create_text(
                x, y, 
                text=digit, 
                font=("Courier", size, "bold"), 
                fill=color
            )
            
            self.rain_digits.append({
                "id": text_id,
                "speed": speed,
                "max_y": height + 30  # When to reset position
            })
        
        # Start the animation
        self.animate_binary_rain(canvas, width, height)
        
        return canvas
    
    def animate_binary_rain(self, canvas, width, height):
        """Animate the binary rain effect"""
        try:
            # Check if canvas still exists
            if not canvas.winfo_exists():
                return
                
            for digit in self.rain_digits:
                try:
                    # Move the digit down
                    canvas.move(digit["id"], 0, digit["speed"])
                    
                    # Get current position
                    pos = canvas.coords(digit["id"])
                    if not pos:  # Skip if the item no longer exists
                        continue
                        
                    # If the digit has moved below the canvas, reset its position
                    if pos[1] > digit["max_y"]:
                        # Reset to a random position above the canvas
                        new_x = random.randint(0, width)
                        new_y = random.randint(-100, -20)
                        canvas.coords(digit["id"], new_x, new_y)
                        
                        # Randomly change the digit
                        if random.random() > 0.5:
                            canvas.itemconfig(digit["id"], text=random.choice(["0", "1"]))
                except:
                    continue  # Skip any digits that cause errors
            
            # Schedule the next animation frame (slower refresh rate)
            self.root.after(100, lambda: self.animate_binary_rain(canvas, width, height))
        except Exception as e:
            print(f"Error in animate_binary_rain: {e}")

    def show_intro(self):
        """Display animated intro screen with binary rain effect"""
        self.clear_screen()
        self.play_sound('welcome')
        
        # Create a container for all elements
        container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        container.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Get the window dimensions - use fixed values if not available yet
        width = self.root.winfo_width() or 800
        height = self.root.winfo_height() or 600
        
        # Create the binary rain animation in the background
        try:
            rain_canvas = self.create_binary_rain_canvas(container, width, height)
            rain_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error creating binary rain: {e}")
        
        # Create a semi-transparent overlay for better text readability
        overlay_frame = tk.Frame(container, bg=self.colors['bg_dark'], bd=0)
        overlay_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Add content to the overlay
        self.show_intro_content(overlay_frame)
        
        # We'll rely on the button click to go to login screen

    def show_intro_content(self, frame):
        """Show the content of the intro screen with binary rain effect and welcome image"""
        # Create a container for the welcome image and content
        image_container = tk.Frame(frame, bg=self.colors['bg_dark'])
        image_container.pack(fill="both", expand=True)
        
        # Display the welcome image as a background
        try:
            welcome_image_label = tk.Label(
                image_container, 
                image=self.images['welcome'], 
                bg=self.colors['bg_dark']
            )
            welcome_image_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error displaying welcome image: {e}")
        
        # Create a semi-transparent overlay for text and buttons
        # Use a slightly transparent background by using a darker color
        overlay_bg = '#1A1225'  # Darker version of bg_dark for better contrast
        overlay = tk.Frame(image_container, bg=overlay_bg)
        overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Add a title at the top
        title_label = tk.Label(
            overlay, 
            text="Python Quiz Master", 
            font=("Arial", 36, "bold"), 
            bg=overlay_bg, 
            fg=self.colors['text']
        )
        title_label.pack(pady=(20, 10))
        
        # Add a subtitle
        subtitle_label = tk.Label(
            overlay, 
            text="Test Your Knowledge • Challenge Your Mind • Become a Python Pro", 
            font=("Arial", 16, "italic"), 
            bg=overlay_bg, 
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Add a message
        message_text = tk.Label(
            overlay, 
            text="Welcome to the ultimate Python Quiz Application!\n\nTest your knowledge across multiple topics, track your progress,\nand challenge yourself to become a Python expert.", 
            font=("Arial", 16), 
            bg=overlay_bg, 
            fg=self.colors['text'],
            justify=tk.CENTER
        )
        message_text.pack(pady=20)
        
        # Add a call to action
        cta_label = tk.Label(
            overlay, 
            text="Are you ready to begin your journey?", 
            font=("Arial", 18, "bold"), 
            bg=overlay_bg, 
            fg=self.colors['text']
        )
        cta_label.pack(pady=(20, 30))
        
        # Add a start button
        start_button = tk.Button(
            overlay, 
            text="Start Your Quiz Adventure!", 
            font=("Arial", 16, "bold"), 
            bg=self.colors['button_primary'], 
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'], 
            activeforeground=self.colors['text'],
            width=25, 
            height=2,
            relief=tk.RAISED,
            bd=3,
            command=self.build_login_screen
        )
        start_button.pack(pady=20)

    def direct_to_menu(self):
        """Directly go to the menu screen without login"""
        print("direct_to_menu called")
        self.current_user = "Guest"  # Set a default user
        messagebox.showinfo("Debug", "Going directly to menu as Guest user")
        self.show_menu()
        
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
                    
            # Also pulse the button color slightly
            if growing:
                # Make button slightly brighter
                r, g, b = button.winfo_rgb(button.cget("background"))
                r = min(65535, int(r * 1.02))
                g = min(65535, int(g * 1.02))
                b = min(65535, int(b * 1.02))
                button.config(background='#%04x%04x%04x' % (r, g, b))
            else:
                # Return to original color
                button.config(background=self.colors['button_primary'])
                
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

        # No welcome image

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
        
        # Attempt to log in
        result = login_user(username, password)
        
        if result:
            self.current_user = username  # Store logged-in user
            messagebox.showinfo("Success", f"Welcome, {username}!", parent=self.root)  # Show success message
            self.show_menu()  # Show the main menu
        else:
            self.play_sound('wrong')
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self.root)  # Show error message
            
            # Ask if the user wants to see the password hint
            response = messagebox.askyesno("Password Hint", "Do you want to see the password hint?", parent=self.root)
            if response:  # User clicked Yes
                hint = get_password_hint(username)  # Fetch the password hint
                if hint:
                    messagebox.showinfo("Password Hint", f"Your password hint is: {hint}", parent=self.root)
                else:
                    messagebox.showinfo("Password Hint", "No password hint set for this account.", parent=self.root)

    def process_login(self, username, password):
        result = login_user(username, password)
        if result:
            self.current_user = username
            self.play_sound('correct')
            self.show_animation('happy', f"Welcome back, {username}! It's great to see you again!", self.show_menu)
            self.root.after(2000, self.show_menu)
        else:
            self.play_sound('wrong')
            self.show_animation('sad', "Oops! I couldn't find those credentials. Would you like to see your password hint?", 
                               lambda: self.ask_for_hint(username))
            self.root.after(2000, lambda: self.ask_for_hint(username))
            
    def ask_for_hint(self, username):
        """Ask if the user wants to see their password hint"""
        response = messagebox.askyesno("Password Hint", "Do you want to see the password hint?", parent=self.root)
        if response:
            self.show_password_hint(username)
        else:
            # If user doesn't want to see the hint, suggest registration
            self.show_animation('sad', "If you don't have an account yet, please register to start your quiz adventure!", 
                               self.build_login_screen)
            self.root.after(2000, self.build_login_screen)

    def show_animation(self, emotion, message, next_action=None):
        """Show animation with a message and optional next action button"""
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
        title_label.pack(pady=20)

        message_text = tk.Label(
            frame, 
            text=message, 
            font=("Arial", 16), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text'], 
            wraplength=500
        )
        message_text.pack(pady=20)
        
        # Add a continue button if there's no next_action scheduled
        if next_action is None:
            continue_button = tk.Button(
                frame,
                text="Continue",
                font=("Arial", 14, "bold"),
                bg=self.colors['button_primary'],
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=15,
                height=1,
                relief=tk.RAISED,
                bd=3,
                command=self.show_menu
            )
            continue_button.pack(pady=20)

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

        # Skip animation and directly process registration
        if register_user(username, password, hint):
            self.current_user = username
            self.play_sound('correct')
            messagebox.showinfo("Registration Successful", f"Welcome, {username}! Your account has been created successfully!", parent=self.root)
            self.show_menu()
        else:
            self.play_sound('wrong')
            messagebox.showerror("Registration Failed", "Could not register your account. The username might already be taken.", parent=self.root)

    def process_registration(self, username, password, hint):
        if register_user(username, password, hint):
            self.current_user = username
            self.play_sound('correct')
            self.show_animation('happy', f"Welcome, {username}! Your account has been created successfully!", 
                               self.show_menu)
            self.root.after(2000, self.show_menu)
        else:
            self.play_sound('wrong')
            self.show_animation('sad', "I couldn't register your account. The username might already be taken.", 
                               self.build_login_screen)
            self.root.after(2000, self.build_login_screen)

    def show_menu(self):
        """Displays the main menu options."""
        self.clear_screen()
        self.play_sound('click')
        
        # Create a container with the themed background
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        # Add a title
        title_label = tk.Label(
            container, 
            text="Quiz Application Menu", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        )
        title_label.pack(pady=20)
        
        # Add a welcome message
        welcome_label = tk.Label(
            container, 
            text=f"Welcome, {self.current_user}!", 
            font=("Arial", 18), 
            bg=self.colors['bg_medium'], 
            fg=self.colors['text']
        )
        welcome_label.pack(pady=10)
        
        # Create a frame for the menu buttons
        menu_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        menu_frame.pack(pady=20, fill="both", expand=True)
        
        # Define menu options
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
        
        # Create all buttons
        for text, command, color in menu_buttons:
            button = tk.Button(
                menu_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                bg=color,
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                width=25,
                height=1,
                relief=tk.RAISED,
                bd=2
            )
            button.pack(pady=5)

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
            messagebox.showinfo("No Topics", "No topics available. Please add some topics first!", parent=self.root)
            self.show_menu()
            return
        
        # Create a frame for the scrollable area
        scroll_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        scroll_frame.pack(pady=10, fill="both", expand=True)
        
        # Create a canvas with scrollbar for the topics
        canvas = tk.Canvas(scroll_frame, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        
        # Create a frame inside the canvas to hold the topics
        topics_frame = tk.Frame(canvas, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        
        # Configure the canvas
        topics_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Set a fixed width for the canvas window
        canvas_width = 400  # Fixed width for the topics area
        canvas.create_window((0, 0), window=topics_frame, anchor="nw", width=canvas_width)
        canvas.configure(yscrollcommand=scrollbar.set, width=canvas_width)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add the topic buttons to the scrollable frame
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
            topic_button.pack(pady=10, padx=20, fill="x")
            
            # Print debug info
            print(f"Added topic button: {display_name}")
        
        # Bind mousewheel to the canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Update the canvas to ensure it shows the content
        topics_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
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
            messagebox.showinfo("No Questions", f"No questions available for this topic with difficulty level {difficulty}.", parent=self.root)
            self.select_difficulty(topic, topic.capitalize())
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
            
            # Save the score - get the topic from the database name
            topic_name = self.questions[0][6]  # This should be the topic name
            save_score(self.current_user, topic_name, percentage_score)
            
            # Show completion screen with confetti for high scores
            if percentage_score >= 80:
                self.play_sound('victory')
                self.show_confetti_celebration(percentage_score)
            else:
                self.play_sound('complete')
                self.show_quiz_completion(percentage_score)
            
            return
            
        # If we're still in the quiz, show the next question
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
        
        # Display the question
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
            
    def show_confetti_celebration(self, percentage_score):
        """Show a celebration screen with animated confetti for high scores"""
        self.clear_screen()
        
        # Create a canvas for the confetti animation
        canvas = tk.Canvas(self.root, bg=self.colors['bg_dark'], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Update the canvas size
        self.root.update()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Add congratulatory text
        canvas.create_text(
            canvas_width // 2, 
            canvas_height // 3,
            text=f"Congratulations!",
            font=("Arial", 36, "bold"),
            fill="#FFD700"  # Gold color
        )
        
        canvas.create_text(
            canvas_width // 2, 
            canvas_height // 2,
            text=f"Your score: {self.score}/{self.rounds} ({percentage_score:.2f}%)",
            font=("Arial", 24),
            fill=self.colors['text']
        )
        
        # Create confetti particles
        confetti_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500", "#800080"]
        confetti_particles = []
        
        for _ in range(100):  # Create 100 confetti particles
            x = random.randint(0, canvas_width)
            y = random.randint(-100, 0)
            size = random.randint(5, 15)
            color = random.choice(confetti_colors)
            speed = random.uniform(1, 5)
            angle = random.uniform(-0.5, 0.5)
            
            particle = canvas.create_rectangle(
                x, y, x + size, y + size,
                fill=color, outline=""
            )
            
            confetti_particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'size': size,
                'speed': speed,
                'angle': angle
            })
        
        # Animate the confetti
        def animate_confetti():
            for particle in confetti_particles:
                # Update position
                particle['y'] += particle['speed']
                particle['x'] += particle['angle']
                
                # Move the particle on canvas
                canvas.move(
                    particle['id'],
                    particle['angle'],
                    particle['speed']
                )
                
                # Rotate the particle (by deleting and recreating)
                if random.random() < 0.05:  # 5% chance to rotate each frame
                    x = particle['x']
                    y = particle['y']
                    size = particle['size']
                    color = canvas.itemcget(particle['id'], 'fill')
                    
                    canvas.delete(particle['id'])
                    particle['id'] = canvas.create_rectangle(
                        x, y, x + size, y + size,
                        fill=color, outline=""
                    )
                
                # Reset particles that fall off the screen
                pos = canvas.coords(particle['id'])
                if pos and len(pos) >= 2 and pos[1] > canvas_height:
                    canvas.move(particle['id'], 0, -canvas_height - size)
                    particle['y'] -= canvas_height
            
            # Continue animation if the canvas still exists
            if canvas.winfo_exists():
                self.root.after(50, animate_confetti)
        
        # Add a button to return to the menu
        button_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        button_frame.place(relx=0.5, rely=0.8, anchor="center")
        
        menu_button = tk.Button(
            button_frame,
            text="Return to Menu",
            font=("Arial", 14),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            command=self.show_menu
        )
        menu_button.pack(pady=10)
        
        # Start the animation
        self.root.after(100, animate_confetti)
    
    def show_quiz_completion(self, percentage_score):
        """Show a standard completion screen for normal scores"""
        self.show_animation('happy', f"Quiz complete! Your score: {self.score}/{self.rounds} ({percentage_score:.2f}%)")
        self.root.after(3000, self.show_menu)

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
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="Add New Question", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # First step: Choose existing topic or create new one
        choice_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        choice_frame.pack(pady=20, fill="x")
        
        choose_button = tk.Button(
            choice_frame,
            text="Choose Existing Topic",
            font=("Arial", 14),
            bg=self.colors['button_success'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            padx=10,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            command=lambda: self.choose_topic_for_question()
        )
        choose_button.pack(side=tk.LEFT, padx=10, expand=True)
        
        create_button = tk.Button(
            choice_frame,
            text="Create New Topic",
            font=("Arial", 14),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            padx=10,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            command=lambda: self.create_topic_for_question()
        )
        create_button.pack(side=tk.LEFT, padx=10, expand=True)
        
        back_button = tk.Button(
            container,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            command=self.show_menu
        )
        back_button.pack(pady=20)

    def choose_topic_for_question(self):
        """Allows the user to choose an existing topic for a new question"""
        self.clear_screen()
        self.play_sound('click')
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="Choose a Topic", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        topics_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        topics_frame.pack(pady=20, fill="both", expand=True)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            self.show_animation('sad', "No topics available. Please create a new topic first!")
            self.root.after(2000, lambda: self.create_topic_for_question())
            return
        
        # Create a scrollable frame for topics
        canvas = tk.Canvas(topics_frame, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(topics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
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
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                activebackground=self.colors['button_primary'],
                activeforeground=self.colors['text'],
                padx=10,
                pady=5,
                width=30,
                relief=tk.RAISED,
                bd=2,
                command=lambda t=raw_name, d=display_name: self.question_form(t, d)
            )
            topic_button.pack(pady=5)
        
        back_button = tk.Button(
            container,
            text="Back",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            command=self.add_new_question
        )
        back_button.pack(pady=10)

    def create_topic_for_question(self):
        """Interface for creating a new topic"""
        self.clear_screen()
        self.play_sound('click')
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text="Create New Topic", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=20)
        
        form_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        form_frame.pack(pady=20, fill="x")
        
        tk.Label(
            form_frame, 
            text="Topic Name:", 
            font=("Arial", 14), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor="w", padx=20)
        
        topic_var = tk.StringVar()
        topic_entry = tk.Entry(form_frame, textvariable=topic_var, font=("Arial", 12), width=40)
        topic_entry.pack(pady=10, padx=20, fill="x")
        
        button_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        button_frame.pack(pady=20)
        
        create_button = tk.Button(
            button_frame,
            text="Create Topic",
            font=("Arial", 14),
            bg=self.colors['button_success'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            padx=10,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            command=lambda: self.process_new_topic(topic_var.get())
        )
        create_button.pack(side=tk.LEFT, padx=10)
        
        back_button = tk.Button(
            button_frame,
            text="Back",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
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
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        tk.Label(
            container, 
            text=f"Add Question to {topic_display}", 
            font=("Arial", 20, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(container, bg=self.colors['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=self.colors['bg_medium'])
        
        form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Difficulty selection
        tk.Label(
            form_frame, 
            text="Difficulty:", 
            font=("Arial", 14), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        difficulty_var = tk.IntVar(value=1)
        difficulty_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        difficulty_frame.pack(fill="x", padx=20, pady=5)
        
        difficulties = [("Easy", 1), ("Medium", 2), ("Hard", 3)]
        for text, value in difficulties:
            tk.Radiobutton(
                difficulty_frame,
                text=text,
                variable=difficulty_var,
                value=value,
                font=("Arial", 12),
                bg=self.colors['bg_medium'],
                fg=self.colors['text'],
                selectcolor=self.colors['bg_light'],
                activebackground=self.colors['bg_light'],
                activeforeground=self.colors['text']
            ).pack(side=tk.LEFT, padx=10)
        
        # Create a more compact layout with two columns
        content_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        content_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Left column for question and correct answer
        left_column = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
        
        # Right column for wrong answers
        right_column = tk.Frame(content_frame, bg=self.colors['bg_medium'])
        right_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5)
        
        # Question text (left column)
        tk.Label(
            left_column, 
            text="Question:", 
            font=("Arial", 12), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(5, 2))
        
        question_var = tk.StringVar()
        question_frame = tk.Frame(left_column, bg=self.colors['bg_medium'])
        question_frame.pack(pady=2, fill="x")
        
        question_entry = tk.Text(question_frame, font=("Arial", 10), height=2, width=40, wrap=tk.WORD)
        question_entry.pack(fill="x", expand=True)
        
        # Correct answer (left column)
        tk.Label(
            left_column, 
            text="Correct Answer:", 
            font=("Arial", 12), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(5, 2))
        
        correct_var = tk.StringVar()
        correct_frame = tk.Frame(left_column, bg=self.colors['bg_medium'])
        correct_frame.pack(pady=2, fill="x")
        
        correct_entry = tk.Text(correct_frame, font=("Arial", 10), height=2, width=40, wrap=tk.WORD)
        correct_entry.pack(fill="x", expand=True)
        
        # Wrong answers (right column)
        wrong_entries = []
        
        # Add a header for the wrong answers column
        tk.Label(
            right_column, 
            text="Wrong Answers:", 
            font=("Arial", 12, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(anchor="w", pady=(5, 10))
        
        for i in range(4):
            tk.Label(
                right_column, 
                text=f"Answer {i+1}:", 
                font=("Arial", 12), 
                bg=self.colors['bg_medium'],
                fg=self.colors['text']
            ).pack(anchor="w", pady=(5, 2))
            
            wrong_frame = tk.Frame(right_column, bg=self.colors['bg_medium'])
            wrong_frame.pack(pady=2, fill="x")
            
            wrong_entry = tk.Text(wrong_frame, font=("Arial", 10), height=2, width=40, wrap=tk.WORD)
            wrong_entry.pack(fill="x", expand=True)
            wrong_entries.append(wrong_entry)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg=self.colors['bg_medium'])
        button_frame.pack(pady=20)
        
        submit_button = tk.Button(
            button_frame,
            text="Submit Question",
            font=("Arial", 14),
            bg=self.colors['button_success'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            padx=10,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            command=lambda: self.submit_question(
                topic_raw,
                difficulty_var.get(),
                question_entry.get("1.0", tk.END).strip(),
                correct_entry.get("1.0", tk.END).strip(),
                [entry.get("1.0", tk.END).strip() for entry in wrong_entries]
            )
        )
        submit_button.pack(side=tk.LEFT, padx=10)
        
        back_button = tk.Button(
            button_frame,
            text="Back",
            font=("Arial", 12),
            bg=self.colors['button_danger'],
            fg=self.colors['text'],
            activebackground=self.colors['button_primary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
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
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Header
        header_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        header_frame.pack(pady=10, fill="x")
        
        tk.Label(
            header_frame, 
            text="Available Topics", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Create a canvas with scrollbar for the topics
        canvas_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        canvas_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        topics_frame = tk.Frame(canvas, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        
        # Configure the canvas
        topics_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=topics_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            tk.Label(
                topics_frame, 
                text="No topics available.", 
                font=("Arial", 16), 
                bg=self.colors['bg_light'],
                fg=self.colors['text']
            ).pack(pady=20, padx=20)
        else:
            # Create a two-column layout for topics
            left_column = tk.Frame(topics_frame, bg=self.colors['bg_light'])
            left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
            
            right_column = tk.Frame(topics_frame, bg=self.colors['bg_light'])
            right_column.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
            
            # Split topics between the two columns
            topic_list = list(topic_mapping.keys())
            half_point = len(topic_list) // 2 + len(topic_list) % 2  # Ceiling division
            
            # Left column topics
            for i, display_name in enumerate(topic_list[:half_point], 1):
                topic_label = tk.Label(
                    left_column,
                    text=f"{i}. {display_name}",
                    font=("Arial", 14),
                    bg=self.colors['bg_light'],
                    fg=self.colors['text'],
                    anchor="w",
                    padx=10
                )
                topic_label.pack(pady=8, fill="x")
            
            # Right column topics
            for i, display_name in enumerate(topic_list[half_point:], half_point + 1):
                topic_label = tk.Label(
                    right_column,
                    text=f"{i}. {display_name}",
                    font=("Arial", 14),
                    bg=self.colors['bg_light'],
                    fg=self.colors['text'],
                    anchor="w",
                    padx=10
                )
                topic_label.pack(pady=8, fill="x")
        
        # Footer with back button
        footer_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        footer_frame.pack(pady=10, fill="x")
        
        back_button = tk.Button(
            footer_frame,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            command=self.show_menu
        )
        back_button.pack(pady=10)

    def delete_topics(self):
        """Interface for deleting topics"""
        self.play_sound('click')
        self.clear_screen()
        
        container = tk.Frame(self.root, bg=self.colors['bg_medium'])
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Header
        header_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        header_frame.pack(pady=10, fill="x")
        
        tk.Label(
            header_frame, 
            text="Delete Topics", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Create a canvas with scrollbar for the topics
        canvas_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        canvas_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        topics_frame = tk.Frame(canvas, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        
        # Configure the canvas
        topics_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=topics_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            tk.Label(
                topics_frame, 
                text="No topics available to delete.", 
                font=("Arial", 16), 
                bg=self.colors['bg_light'],
                fg=self.colors['text']
            ).pack(pady=20, padx=20)
        else:
            # Single column layout for delete topics
            for display_name, raw_name in topic_mapping.items():
                topic_frame = tk.Frame(topics_frame, bg=self.colors['bg_light'])
                topic_frame.pack(pady=5, padx=10, fill="x")
                
                tk.Label(
                    topic_frame,
                    text=display_name,
                    font=("Arial", 14),
                    bg=self.colors['bg_light'],
                    fg=self.colors['text'],
                    anchor="w"
                ).pack(side=tk.LEFT, padx=10)
                
                delete_button = tk.Button(
                    topic_frame,
                    text="Delete",
                    font=("Arial", 12),
                    bg=self.colors['button_danger'],
                    fg=self.colors['text'],
                    activebackground=self.colors['button_primary'],
                    activeforeground=self.colors['text'],
                    relief=tk.RAISED,
                    bd=2,
                    command=lambda t=display_name: self.confirm_delete_topic(t)
                )
                delete_button.pack(side=tk.RIGHT, padx=10)
        
        # Footer with back button
        footer_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        footer_frame.pack(pady=10, fill="x")
        
        back_button = tk.Button(
            footer_frame,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            command=self.show_menu
        )
        back_button.pack(pady=10)

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
        
        # Header
        header_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        header_frame.pack(pady=10, fill="x")
        
        tk.Label(
            header_frame, 
            text="View Topic Questions", 
            font=("Arial", 24, "bold"), 
            bg=self.colors['bg_medium'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Get all topics
        topic_mapping = get_topics()
        
        if not topic_mapping:
            self.show_animation('sad', "No topics available.")
            self.root.after(1500, self.show_menu)
            return
        
        # Create a canvas with scrollbar for the topics
        canvas_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        canvas_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        topics_frame = tk.Frame(canvas, bg=self.colors['bg_light'], bd=2, relief=tk.RAISED)
        
        # Configure the canvas
        topics_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=topics_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create a two-column layout for topics
        left_column = tk.Frame(topics_frame, bg=self.colors['bg_light'])
        left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        
        right_column = tk.Frame(topics_frame, bg=self.colors['bg_light'])
        right_column.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)
        
        # Split topics between the two columns
        topic_items = list(topic_mapping.items())
        half_point = len(topic_items) // 2 + len(topic_items) % 2  # Ceiling division
        
        # Left column topics
        for display_name, raw_name in topic_items[:half_point]:
            topic_button = tk.Button(
                left_column,
                text=display_name,
                font=("Arial", 12),
                bg=self.colors['button_primary'],
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=5,
                pady=3,
                width=15,
                command=lambda t=raw_name, d=display_name: self.show_topic_questions(t, d)
            )
            topic_button.pack(pady=5, fill="x")
        
        # Right column topics
        for display_name, raw_name in topic_items[half_point:]:
            topic_button = tk.Button(
                right_column,
                text=display_name,
                font=("Arial", 12),
                bg=self.colors['button_primary'],
                fg=self.colors['text'],
                activebackground=self.colors['button_secondary'],
                activeforeground=self.colors['text'],
                padx=5,
                pady=3,
                width=15,
                command=lambda t=raw_name, d=display_name: self.show_topic_questions(t, d)
            )
            topic_button.pack(pady=5, fill="x")
        
        # Footer with back button
        footer_frame = tk.Frame(container, bg=self.colors['bg_medium'])
        footer_frame.pack(pady=10, fill="x")
        
        back_button = tk.Button(
            footer_frame,
            text="Back to Menu",
            font=("Arial", 12),
            bg=self.colors['button_primary'],
            fg=self.colors['text'],
            activebackground=self.colors['button_secondary'],
            activeforeground=self.colors['text'],
            relief=tk.RAISED,
            bd=2,
            command=self.show_menu
        )
        back_button.pack(pady=10)

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
        messagebox.showinfo("Logout", "You have been logged out successfully!", parent=self.root)
        self.build_login_screen()

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
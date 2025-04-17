from tkinter import simpledialog, messagebox

def user_exists(username):
    """Checks if a user exists in the database."""
    from db import connect_db  # Import inside the function to avoid circular import
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
    conn.close()
    return user is not None


def check_password(username, password):
    """Checks if the password for a given username matches the stored password in the database."""
    from db import connect_db  # Import inside the function to avoid circular import
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        stored_password = cursor.fetchone()
    conn.close()
    
    if stored_password and stored_password[0] == password:
        return True
    return False

def get_password_hint(username):
    """Fetches the password hint for the user."""
    from db import connect_db
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT hint FROM users WHERE username = %s", (username,))
        hint = cursor.fetchone()
    conn.close()

    if hint and hint[0]:
        return hint[0]  # Return the password hint
    return None  # Return None if no hint is found




def login(username=None):
    """Handles the user login process, including username and password."""
    if username is None:
        username = input("Enter your username: ").strip()

    if not user_exists(username):
        print("❌ User not found. Please register first.")
        return None
    
    password = input("Enter your password: ").strip()

    if not check_password(username, password):
        print("❌ Incorrect password. Please try again.")
        
        # Show password hint if it exists
        hint = get_password_hint(username)
        if hint:
            print(f"💡 Hint: {hint}")
        return None
    
    print(f"✅ Welcome back, {username}!")
    return username


def create_user_account():
    """Registers a new user account in the PostgreSQL database or prompts to login if the username exists."""
    from db import connect_db  # Import inside the function to avoid circular import
    username = input("Enter your desired username: ").strip()

    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"❌ Username '{username}' already exists.")
            conn.close()

            choice = input("Would you like to login with this username? Enter '1' to login or '2' to choose a different username: ").strip()
            if choice == '1':
                return login(username)
            elif choice == '2':
                print("Please choose a different username.")
                return None
            else:
                print("Invalid choice. Please try again.")
                return None

    password = input(f"Create a password for '{username}': ").strip()
    
    # Ask for password hint
    hint = input("Enter a password hint (optional): ").strip()

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password, hint) VALUES (%s, %s, %s)", (username, password, hint))
        conn.commit()
        print(f"✅ User '{username}' registered successfully!")

    conn.close()
    return username


def change_user():
    """Logs out the current user and allows logging in with a different account."""
    print("You have logged out successfully.")
    logged_in_user = None
    
    while logged_in_user is None:
        print("\n=== Welcome to the Quiz Application ===")
        print("1. Log in with an existing account")
        print("2. Register a new account")
        choice = input("Would you like to log in or register a new account? Enter 1 to log in, 2 to register: ").strip()

        if choice == "1":
            logged_in_user = login()
        elif choice == "2":
            registered_user = create_user_account()
            if registered_user:
                print(f"Welcome {registered_user}!")
                logged_in_user = registered_user
            else:
                print("Registration failed. Try again.")
        else:
            print("Invalid choice. Please select 1 to log in or 2 to register.")
    
    return logged_in_user


### GUI

def login_user(username, password, hint=None):
    """Login a user and retrieve password using a hint if forgotten"""
    from db import connect_db
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check if the username exists
        cursor.execute("SELECT username, password, hint FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user is None:
            print("User not found")  # Debugging log
            return False  # Username not found

        stored_username, stored_password, stored_hint = user
        print(f"User found: {stored_username}, Password: {stored_password}")  # Debugging log

        # Check if password matches
        if password == stored_password:
            print("Password matches!")  # Debugging log
            return True  # Successful login
        else:
            print("Password mismatch")  # Debugging log
            if hint is None:
                hint = simpledialog.askstring("Password Hint", "Forgot your password? Enter your hint:")

            # Check if the hint matches
            if hint == stored_hint:
                print("Hint matches!")  # Debugging log
                return True  # Password match with hint
            else:
                print("Hint mismatch")  # Debugging log
                return False  # Password and hint do not match
    finally:
        conn.close()

def register_user(username, password, hint=None):
    """Register a new user with an optional password hint"""
    from db import connect_db
    conn = connect_db()
    
    with conn.cursor() as cursor:
        # Check if the username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            return False  # User already exists
        
        # Ask for a password hint if not provided
        if hint is None:
            hint = simpledialog.askstring("Password Hint", "Enter a password hint (optional):")
        
        if hint is None:  # If the user cancels the hint prompt
            hint = ""  # Default to an empty string if no hint is provided

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password, hint) VALUES (%s, %s, %s)", (username, password, hint))
        conn.commit()

    conn.close()
    messagebox.showinfo("Success", f"User '{username}' registered successfully!")
    return True




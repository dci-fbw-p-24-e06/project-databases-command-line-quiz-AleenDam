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

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
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

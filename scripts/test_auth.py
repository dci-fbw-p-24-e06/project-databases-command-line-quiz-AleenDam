from auth import login_user, register_user
from db import connect_db

# Test user registration and login
def test_auth():
    try:
        # Check if users table exists
        conn = connect_db()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    hint TEXT
                );
            """)
            conn.commit()
            
            # Check if test user exists
            cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
            if cursor.fetchone():
                print("Test user already exists")
            else:
                # Register a test user
                register_user('testuser', 'testpass', 'test hint')
                print("Test user registered")
            
            # Try to login with the test user
            login_result = login_user('testuser', 'testpass')
            print(f"Login result: {login_result}")
            
            # List all users
            cursor.execute("SELECT username, password, hint FROM users")
            users = cursor.fetchall()
            print("All users:")
            for user in users:
                print(f"Username: {user[0]}, Password: {user[1]}, Hint: {user[2]}")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_auth()
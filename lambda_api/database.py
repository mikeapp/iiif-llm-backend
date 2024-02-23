import pg8000
from shared_lib import get_secret


def get_connection():
    credentials = get_secret("ai/database")
    return pg8000.connect(
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['database'],
        host=credentials['host'],
        ssl_context=True)


# Users
def create_user_record(username, email_address, credits):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Prepare SQL statement
        sql = """INSERT INTO users (username, email_address, credits) 
                 VALUES (%s, %s, %s)"""
        # Execute SQL statement
        cursor.execute(sql, (username, email_address, credits))
        # Commit the transaction
        conn.commit()
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def get_user_by_username(username):
    try:
        # Connect to the database
        conn = get_connection();
        cursor = conn.cursor();

        # Prepare SQL statement
        sql = """SELECT * FROM users WHERE username = %s"""

        # Execute SQL statement
        cursor.execute(sql, (username,))

        # Fetch the user record
        user_record = cursor.fetchone()

        if user_record:
            # Print or return the user record
            print("User found:", user_record)
            return user_record
        else:
            print("User not found.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
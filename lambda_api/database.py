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
def create_user_record(conn, username, email_address, credits):
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

def get_user_by_username(conn, username):
    try:
        cursor = conn.cursor();
        sql = """SELECT username, email_address, credits  FROM users WHERE username = %s"""
        cursor.execute(sql, (username,))
        user_record = cursor.fetchone()
        if user_record:
            return user_record
        else:
            print("User not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()


# Credits used
def get_credits_used_by_username(conn, username):
    try:
        cursor = conn.cursor();
        sql = """SELECT username, credits_used FROM user_credits_used WHERE username = %s"""
        cursor.execute(sql, (username,))
        credits_used = cursor.fetchone()
        if credits_used:
            return credits_used
        else:
            print("UserCreditsUsed not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()

# Activities
def insert_activity_record(conn, username, object_id, service_provider, credits_used):
    try:
        cursor = conn.cursor()
        sql = """INSERT INTO activities (username, object_id, service_provider, credits_used) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (username, object_id, service_provider, credits_used))
        conn.commit()
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        # Close the cursor and connection
        cursor.close()

# OCR
def insert_ocr_record(conn, image_id, object_id, text_engine='TEXTRACT', text_content=None):
    try:
        cursor = conn.cursor()
        sql = """INSERT INTO ocr (image_id, object_id, text_engine, text_content) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (image_id, object_id, text_engine, text_content))
        conn.commit()
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        # Close the cursor and connection
        cursor.close()


def get_ocr(conn, image_id, object_id, text_engine='Textract'):
    try:
        cursor = conn.cursor()
        sql = """SELECT * FROM ocr WHERE image_id = %s AND object_id = %s AND text_engine = %s"""
        cursor.execute(sql, (image_id, object_id, text_engine))
        record = cursor.fetchone()
        if record:
            return record
        else:
            print("Record not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()


# Generic Prompt
def get_generic_prompt_by_key(conn, prompt_key):
    try:
        cursor = conn.cursor()
        sql = """SELECT * FROM generic_prompts WHERE prompt_key = %s"""
        cursor.execute(sql, (prompt_key,))
        prompt_record = cursor.fetchone()
        if prompt_record:
            return prompt_record
        else:
            print("Prompt not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()

def get_generic_prompts(conn):
    try:
        cursor = conn.cursor()
        sql = """SELECT * FROM generic_prompts ORDER BY prompt_label"""
        cursor.execute(sql)
        prompt_record = cursor.fetchone()
        if prompt_record:
            return prompt_record
        else:
            print("Prompts not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
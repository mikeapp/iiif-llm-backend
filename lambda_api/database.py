import pg8000
from shared_lib import get_secret

DEFAULT_CREDITS = 500

def auth_user(cognito):
    username = cognito['username']
    groups = cognito['groups']
    TARGET_GROUP = 'ai-user'
    if isinstance(groups, str) and (groups == TARGET_GROUP):
        return username
    if isinstance(groups, list) and TARGET_GROUP in groups:
        return username
    raise Exception('User not in authorized group')

# Utitliy
def get_connection():
    credentials = get_secret("ai/database")
    return pg8000.connect(
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['database'],
        host=credentials['host'],
        ssl_context=True)


def result_to_dict(cursor, rows):
    keys = [k[0] for k in cursor.description]
    result = {}
    for index, row in enumerate(rows):
        result[keys[index]] = row
    return result

def list_to_dicts(cursor, list):
    result = []
    for item in list:
        result.append(result_to_dict(cursor, item))
    return result

# Convenience
def find_or_create_user(event, conn):
    username = event['username']
    user = get_user_by_username(conn, username)
    if user is None:
        email = event['email']
        create_user_record(conn, username, email, DEFAULT_CREDITS)
        user = get_user_by_username(conn, username)
    return user

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

def get_user_by_username(conn, username):
    try:
        cursor = conn.cursor();
        sql = """SELECT username, email_address, credits  FROM users WHERE username = %s"""
        cursor.execute(sql, (username,))
        user_record = cursor.fetchone()
        if user_record:
            return result_to_dict(cursor, user_record)
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
            return result_to_dict(cursor, credits_used)
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


def get_ocr(conn, object_id, text_engine='TEXTRACT'):
    try:
        cursor = conn.cursor()
        sql = """SELECT object_id, image_id, text_engine, text_content FROM ocr WHERE object_id = %s AND text_engine = %s"""
        cursor.execute(sql, (object_id, text_engine))
        record = cursor.fetchall()
        if record:
            return list_to_dicts(cursor, record)
        else:
            print("Record not found.")
            return None
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()


# Generic Prompt
def get_generic_prompt_by_key(conn, prompt_key):
    try:
        cursor = conn.cursor()
        sql = """SELECT prompt_key, prompt_label, prompt_description, prompt_text FROM generic_prompts WHERE prompt_key = %s"""
        cursor.execute(sql, (prompt_key,))
        prompt_record = cursor.fetchone()
        if prompt_record:
            return result_to_dict(cursor, prompt_record)
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
        sql = """SELECT prompt_key, prompt_label, prompt_description, prompt_text FROM generic_prompts ORDER BY prompt_label"""
        cursor.execute(sql)
        prompt_records = cursor.fetchall()
        if prompt_records:
            return list_to_dicts(cursor, prompt_records)
        else:
            print("Prompts not found.")
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
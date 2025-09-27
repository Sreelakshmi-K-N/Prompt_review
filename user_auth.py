import mysql.connector
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="prompt_review"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hash_password(password)))
    conn.commit()
    cursor.close()
    conn.close()

def authenticate_user(username, password):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="prompt_review"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False
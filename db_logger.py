import mysql.connector
import json

def log_prompt(prompt, verdict, reason, tone, costar, llm_response):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root@123",
            database="prompt_review"
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO logs (prompt, verdict, reason, tone, costar, llm_response)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            prompt,
            verdict,
            reason,
            tone,
            json.dumps(costar),
            llm_response
        ))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[DB Error] {e}")
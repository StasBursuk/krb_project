import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Завантажуємо налаштування з .env
load_dotenv()

def get_db_connection():
    """Створює та повертає підключення до бази даних."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            cursor_factory=RealDictCursor # Повертає результати як словники
        )
        return conn
    except Exception as e:
        print(f"Критична помилка підключення до БД: {e}")
        return None

def init_db():
    """Створює необхідні таблиці, якщо їх ще немає."""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(255),
                username VARCHAR(255),
                ip_address VARCHAR(50),
                ping_status TEXT,
                registry_category VARCHAR(100),
                problem_description TEXT,
                screenshot_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
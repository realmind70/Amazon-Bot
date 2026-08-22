import sqlite3

DB_FILE = "amazon_deals.db"

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_deals (
            product_url TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_sent_product(product_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sent_deals (product_url) VALUES (?)", (product_url,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def is_product_sent(product_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_deals WHERE product_url = ?", (product_url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


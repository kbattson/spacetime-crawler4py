import sqlite3

def setup_db():
    conn = sqlite3.connect('crawler_data.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        url TEXT PRIMARY KEY,
        content TEXT
    )
    ''')
    conn.commit()
    return conn

def is_visited(conn, url):
    c = conn.cursor()
    c.execute("SELECT 1 FROM pages WHERE url = ?", (url,))
    return c.fetchone() is not None

def store_page(conn, url, content):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO pages (url, content) VALUES (?, ?)", (url, content))
    except sqlite3.IntegrityError:
        # url already in db
        pass
        

    conn.commit()

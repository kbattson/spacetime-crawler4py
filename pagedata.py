import sqlite3

def init_db():
    conn = sqlite3.connect('crawler_data.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        url TEXT PRIMARY KEY,
        content TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS blacklist (
        url TEXT PRIMARY KEY,
        error TEXT
    )
    ''')
    conn.commit()
    conn.close()

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

def is_blacklisted(conn, url):
    c = conn.cursor()
    c.execute("SELECT 1 FROM blacklist WHERE url = ?", (url,))
    return c.fetchone() is not None

def blacklist_url(conn, url, error):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO blacklist (url, error) VALUES (?, ?)", (url, error))
    except sqlite3.IntegrityError:
        # url already in blacklist (kind of a problem: why did it try and blacklist and blisted page???)
        pass
    conn.commit()

def reset_db():
    conn = sqlite3.connect('crawler_data.db')
    c = conn.cursor()
    while True:
        response = input("Reset crawler page data? (reset if starting crawl from scratch) [y/n] ")
        if response == 'y':
            c.execute('DROP TABLE IF EXISTS pages')
            break
        elif response == 'n':
            break

    while True:
        response = input("Reset crawler blacklist? (don't reset, blacklist should be kept over multiple crawls) [y/n] ")
        if response == 'y':
            c.execute('DROP TABLE IF EXISTS blacklist')
            break
        elif response == 'n':
            break

    conn.commit()
    conn.close()









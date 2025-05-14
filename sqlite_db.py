import sqlite3

def init_db():
    conn = sqlite3.connect('eventlink.db')
    c = conn.cursor()

    # Services table
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            rating INTEGER,
            images TEXT
        )
    ''')

    # Bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            event_date TEXT,
            event_time TEXT,
            provider_name TEXT,
            message TEXT,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()

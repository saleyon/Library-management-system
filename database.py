import sqlite3

DATABASE_NAME = "library.db"

def get_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign key constraints
    return conn

def initialize_database():
    """Creates the necessary tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Books Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                available_copies INTEGER NOT NULL CHECK (available_copies >= 0)
            )
        """)
        
        # 2. Members Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)
        
        # 3. Loans Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                member_id INTEGER,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        # 4. Fines Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_id INTEGER UNIQUE,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'Unpaid' CHECK (status IN ('Unpaid', 'Paid')),
                FOREIGN KEY (loan_id) REFERENCES loans(id)
            )
        """)
        
        conn.commit()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
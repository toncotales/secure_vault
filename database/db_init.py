import sqlite3


DB_PATH = "database/vault.db"


def initialize_database():
    """Initialize the SQLite database and create the necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the online_accounts table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS online_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            owner TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
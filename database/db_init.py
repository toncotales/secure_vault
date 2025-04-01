import sqlite3


DB_PATH = "database/vault.db"


def initialize_database():
    """Initialize the SQLite database and create the necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the debit_cards table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS debit_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_number TEXT NOT NULL UNIQUE,
            cardholder_name TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            cvv TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create the online_accounts table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS online_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create the identification_credentials table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS identification_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_type TEXT NOT NULL,
            id_number TEXT NOT NULL UNIQUE,
            issued_by TEXT NOT NULL,
            issued_date DATE NOT NULL,
            expiry_date DATE
        );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
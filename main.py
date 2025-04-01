from database.db_init import initialize_database, DB_PATH
from database.db_manager import DatabaseManager


def main():
    # Initialize the database
    initialize_database()

    # Create a DatabaseManager instance
    db_manager = DatabaseManager(DB_PATH)

    # List all tables in the database
    tables = db_manager.list_tables()
    print(tables)

    # Close the database connection
    db_manager.close()


if __name__ == "__main__":
    main()
import sqlite3


DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
DB_OPERATION_ERROR = "DB_OPERATION_ERROR"


class SQLiteDatabaseConnection:
    def __init__(self, database_file: str):
        self.database_file = database_file
        self.connection = self.connect()

    def connect(self):
        try:
            conn = sqlite3.connect(self.database_file)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON;")
            return conn
        
        except Exception:
            return DB_CONNECTION_ERROR
        
    def execute_query(self, query: str, params: dict = {}, fetchall: bool = False):
        try:
            with self.connection as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetchall:
                    return cursor.fetchall()
                else:
                    return (cursor.fetchone() or bool(cursor.rowcount))
                
        except Exception as e:
            return (DB_OPERATION_ERROR, e)
                
    def close(self):
        if self.connection != DB_CONNECTION_ERROR:
            self.connection.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DatabaseManager(SQLiteDatabaseConnection):
    def __init__(self, database_file: str):
        super().__init__(database_file)
        
    def list_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        tables = self.execute_query(query, fetchall=True)
        return [table['name'] for table in tables] if tables else tables
    
    def list_columns(self, table: str):
        query = f"PRAGMA table_info({table});"
        columns = self.execute_query(query, fetchall=True)
        return [column['name'] for column in columns] if columns else columns
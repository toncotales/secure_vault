import sqlite3
import csv


DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
DB_OPERATION_ERROR = "DB_OPERATION_ERROR"


class SQLiteDatabaseConnection:
    def __init__(self, database_file: str):
        self.database_file = database_file
        self.connection = self.connect()

    def connect(self):
        try:
            conn = sqlite3.connect(self.database_file)
            conn.row_factory = self.dict_factory
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
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

    def dict_factory(self, cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

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

    def fetchall(self, table: str):
        return self.execute_query(f"SELECT * FROM {table};", fetchall=True)

    def insert(self, table: str, data: dict):
        columns = ', '.join(data.keys())
        placeholders = ', '.join([f":{k}" for k in data.keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders});"
        return self.execute_query(query, data)
    
    def search(self, table: str, data: dict):
        conditions = ' AND '.join([f"{k}='{v}'" for k, v in data.items()])
        query = f"SELECT * FROM {table} WHERE {conditions};"
        return self.execute_query(query, data, fetchall=True)
    
    def update(self, table: str, old: dict, new: dict):
        updates = ', '.join([f"{k}=:new_{k}" for k in new.keys()])
        conditions = ' AND '.join([f"{k}=:old_{k}" for k in old.keys()])
        query = f"UPDATE {table} SET {updates} WHERE {conditions};"
        params = {f"new_{k}": v for k,v in new.items()} | {f"old_{k}": v for k,v in old.items()}
        return self.execute_query(query, params)
    
    def delete(self, table: str, data: dict):
        result = self.search(table, data)
        if isinstance(result, list):
            if len(result) == 1:
                conditions = ' AND '.join([f"{k}=:{k}" for k in data.keys()])
                query = f"DELETE FROM {table} WHERE {conditions};"
                return self.execute_query(query, data)
            elif len(result) > 1:
                return (DB_OPERATION_ERROR, "Multiple records found for deletion.")
            else:
                return (DB_OPERATION_ERROR, "No records found for deletion.")
        return result

    def insert_individually(self, table: str, data_list: list = []) -> tuple:
        """Insert records one at a time."""
        failed_count = 0
        insert_count = 0
        if isinstance(data_list, list):
            for data in data_list:
                if isinstance(data, dict):
                    result = self.insert(table, data)
                    if not result or isinstance(result, tuple):
                        failed_count += 1
                    else:
                        insert_count += 1
        return (insert_count, failed_count)
    
    def bulk_insert(self, table: str, data_list: list = []):
        """Insert multiple records in a single query."""
        if isinstance(data_list, list) and len(data_list) > 0:
            if isinstance(data_list[0], dict):
                columns = ', '.join(data_list[0].keys())
                placeholders = ', '.join([f":{k}" for k in data_list[0].keys()])
                query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders});"
                try:
                    with self.connection as conn:
                        cursor = conn.cursor()
                        cursor.executemany(query, data_list)
                    return True

                except Exception as e:
                    return (DB_OPERATION_ERROR, e)
                
    def count(self, table: str, data: dict = None):
        """Count records in a table with optional conditions."""
        if isinstance(data, dict):
            conditions = " WHERE " + " AND ".join([f"{k}=:{k}" for k in data.keys()])
        else: 
            conditions = ''
        query = f"SELECT COUNT(*) as count FROM {table}{conditions};"
        result = self.execute_query(query, data if conditions else {})
        return result['count'] if isinstance(result, dict) else result
    
    def create_index(self, table: str, column: str, unique: bool = False):
        """Create an index on a table column."""
        index_name = f"idx_{table}_{column}"
        unique = "UNIQUE" if unique else ""
        query = f"CREATE {unique} INDEX IF NOT EXISTS {index_name} ON {table} ({column});"
        return self.execute_query(query)
    
    def backup(self, backup_file: str):
        """Backup database to another file."""
        try:
            with sqlite3.connect(backup_file) as backup_conn:
                self.connection.backup(backup_conn)
            return True
        except Exception:
            return False

    def restore(self, backup_file: str):
        """Restore database from a backup file."""
        try:
            self.close()
            with sqlite3.connect(backup_file) as backup_conn:
                with sqlite3.connect(self.database_file) as conn:
                    backup_conn.backup(conn)

            self.connection = self.connect()
            return True
        except Exception:
            return False
        
    def export_to_csv(self, table: str, file_path: str):
        """Export table data to a CSV file."""
        data = self.fetchall(table)
        columns = self.list_columns(table)
        try:
            if isinstance(data, list) and len(data) > 0:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(data)
                return True
            raise TypeError
        except Exception:
            return False

    def import_from_csv(self, table: str, file_path: str):
        """Import data from a CSV file into the database table."""
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                csv_columns = reader.fieldnames
                if table in self.list_tables():
                    if csv_columns == self.list_columns(table):
                        return self.bulk_insert(table, list(reader))
            raise ValueError
        except Exception:
            return False
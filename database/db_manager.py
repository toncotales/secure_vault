from database.db_sqlite import DatabaseManager
from database.db_sqlite import DB_CONNECTION_ERROR, DB_OPERATION_ERROR
from database.db_init import DB_PATH
from services.encryption import EncryptionService



class DatabaseManager(DatabaseManager):
    def __init__(self, db_path: str):
        super().__init__(db_path)

    
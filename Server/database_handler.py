import threading
import os
import sqlite3
import uuid
from datetime import datetime


DATABASE_FILE = "server.db"
DATABASE_SCHEMA = """
        CREATE TABLE IF NOT EXISTS clients (
            ClientID BLOB(16) PRIMARY KEY,
            Name TEXT NOT NULL,
            PublicKey BLOB(160) NOT NULL,
            LastSeen TEXT NOT NULL,
            AESKey BLOB(16) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS files (
            ID BLOB(16) PRIMARY KEY,
            FileName TEXT NOT NULL,
            PathName TEXT NOT NULL,
            Verified BOOLEAN NOT NULL DEFAULT 0
        );
    """


class DatabaseHandler:
    def __init__(self):
        self.lock = threading.Lock()
        self.connection = None
        if self.is_database_exists():
            try:
                self.connection = sqlite3.connect(DATABASE_FILE)
            except sqlite3.Error as e:
                print(f"Error connecting to database '{DATABASE_FILE}': {e}")

        else:
            print("Creating a new database...")
            try:
                self.connection = sqlite3.connect(DATABASE_FILE)
                self.connection.executescript(DATABASE_SCHEMA)
                self.connection.commit()
                print(f"Database '{DATABASE_FILE}' created successfully")
            except sqlite3.Error as e:
                print(f"Error creating database '{DATABASE_FILE}': {e}")

    def __enter__(self):
        if not self.is_database_exists():
            self.create_database()
        self.connection = sqlite3.connect(self.DATABASE_FILE)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            self.connection.close()

    def create_database(self):
        with self.connection as connection:
            connection.executescript(self.DATABASE_SCHEMA)

    def register_client(self, client_name):

        # Generate a new client id:
        generated_uuid = uuid.uuid4()
        # Ensure UUID doesn't exceed 16 bytes
        client_id = generated_uuid.bytes[:16]

        public_key = str()
        aes_key = str()
        last_seen = self.get_last_seen()

        with self.lock:  # Avoid a case of concurrent same username registration
            # Acquire the lock to ensure mutual exclusion
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO clients (ClientID, Name, PublicKey, LastSeen, AESKey) VALUES (?, ?, ?, ?, ?)",
                    (client_id, client_name, public_key, last_seen, aes_key))
                connection.commit()

    @staticmethod
    def is_database_exists():
        return os.path.isfile(DATABASE_FILE)

    def is_client_exists(self, client_name):
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM clients WHERE Name = ?", (client_name,))
                row = cursor.fetchone()
                return row is not None and row[1] != ""

    def is_RSA_key_exists(self, client_name):
        if not self.is_client_exists(client_name):
            return False

        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT PublicKey FROM clients WHERE Name = ?", (client_name,))
                row = cursor.fetchone()
                return row is not None and row[0] != ""

    def get_public_RSA_key(self, client_name):
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                query = "SELECT PublicKey FROM clients WHERE Name = ?"
                cursor.execute(query, (client_name,))
                result = cursor.fetchone()
                return result[0]

    def get_client_id(self, client_name):
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                query = "SELECT ClientID FROM clients WHERE Name = ?"
                cursor.execute(query, (client_name,))
                result = cursor.fetchone()
                return result[0]

    def get_client_name(self, client_id):
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                query = "SELECT Name FROM clients WHERE ClientID = ?"
                cursor.execute(query, (client_id,))
                result = cursor.fetchone()
                return result[0] if result is not None else None

    def get_AES_key(self, client_name):
        client_name = str(client_name)
        with self.connection as connection:
            cursor = connection.cursor()
            query = "SELECT AESKey FROM clients WHERE Name = ?"
            cursor.execute(query, (client_name,))
            result = cursor.fetchone()
            return result[0]

    def update_public_RSA_key(self, client_name, public_key):
        client_name = str(client_name)

        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE clients SET PublicKey = ? WHERE Name = ?", (public_key, client_name))
                connection.commit()

    def update_AES_key(self, client_name, new_AES_key):
        client_name = str(client_name)
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE clients SET AESKey = ? WHERE Name = ?", (new_AES_key, client_name))
                connection.commit()

    def update_last_seen(self, client_id):
        client_id = str(client_id)
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                last_seen = str(datetime.now())
                cursor.execute(
                    "UPDATE clients SET LastSeen = ? WHERE ClientID = ?", (last_seen, client_id))
                connection.commit()

    @staticmethod
    def get_last_seen():
        current_time = datetime.now()
        return current_time.strftime("%Y-%m-%d %H:%M:%S")

    def update_file_info(self, client_id, client_name, file_name):
        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                file_path = os.path.join(client_name, file_name)
                cursor.execute(
                    "UPDATE files SET FileName = ?, PathName = ? WHERE ID = ?", (str(
                        file_name), str(file_path), str(client_id)))
                connection.commit()

    def update_crc(self, client_id, crc):

        with self.lock:
            with self.connection as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE files SET Verified = ? WHERE ID = ?", (crc, str(client_id)))
                connection.commit()

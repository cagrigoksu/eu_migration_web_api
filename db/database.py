import os
from contextlib import contextmanager
from datetime import datetime, timedelta
import uuid
from pysqlcipher3 import dbapi2 as sqlite
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class Database:
    #* Database manager for API keys
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.encryption_key = Config.DB_ENCRYPTION_KEY
        self._ensure_directory()
    
    #* ensure database dir exists
    def _ensure_directory(self):
       
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        #* Context manager for db connections
        conn = None
        try:
            conn = sqlite.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA key = '{self.encryption_key}';")
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_db(self):
        #! init db tables
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # apikeys table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS apikeys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        issue_date TEXT NOT NULL,
                        expiry_date TEXT NOT NULL,
                        user_email TEXT UNIQUE NOT NULL,
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # api_usage table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                        response_code INTEGER,
                        FOREIGN KEY (api_key) REFERENCES apikeys(key)
                    )
                ''')
                
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def create_api_key(self, user_email):
        #* create a new api key for a user
        try:
            new_key = str(uuid.uuid4())
            issue_date = datetime.now()
            expiry_date = issue_date + timedelta(days=Config.API_KEY_EXPIRY_DAYS)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO apikeys (key, issue_date, expiry_date, user_email, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (
                    new_key,
                    issue_date.strftime('%Y-%m-%d %H:%M:%S'),
                    expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                    user_email
                ))
            
            logger.info(f"API key created for user: {user_email}")
            return new_key
        except sqlite.IntegrityError:
            # then user already has a key, return existing
            return self.get_user_key(user_email)
        except Exception as e:
            logger.error(f"Failed to create API key: {str(e)}")
            raise
    
    def get_user_key(self, user_email):
        #* get active api key for a user
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT key FROM apikeys 
                    WHERE user_email = ? AND is_active = 1
                    ORDER BY created_at DESC LIMIT 1
                ''', (user_email,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get user key: {str(e)}")
            return None
    
    def is_valid_api_key(self, api_key):
        
        # validate api key
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT expiry_date, is_active FROM apikeys WHERE key = ?
                ''', (api_key,))
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                expiry_date_str, is_active = result
                
                if not is_active:
                    return False
                
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d %H:%M:%S')
                return datetime.now() < expiry_date
        except Exception as e:
            logger.error(f"Failed to validate API key: {str(e)}")
            return False
    
    def deactivate_api_key(self, api_key):
        #* deactivate api key
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE apikeys SET is_active = 0 WHERE key = ?
                ''', (api_key,))
            logger.info(f"API key deactivated: {api_key[:8]}...")
        except Exception as e:
            logger.error(f"Failed to deactivate API key: {str(e)}")
            raise
    
    def log_api_usage(self, api_key, endpoint, response_code):
        #* log API usage
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_usage (api_key, endpoint, response_code)
                    VALUES (?, ?, ?)
                ''', (api_key, endpoint, response_code))
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    def get_api_stats(self, api_key=None):
        #* get API usage statistics
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if api_key:
                    cursor.execute('''
                        SELECT endpoint, COUNT(*) as count
                        FROM api_usage
                        WHERE api_key = ?
                        GROUP BY endpoint
                    ''', (api_key,))
                else:
                    cursor.execute('''
                        SELECT endpoint, COUNT(*) as count
                        FROM api_usage
                        GROUP BY endpoint
                    ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get API stats: {str(e)}")
            return []

# glob db instance
db = Database()

def init_db():
    #! init database
    db.init_db()

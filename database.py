import sqlite3
import hashlib
from datetime import datetime

class BotDatabase:
    def __init__(self, db_path='bot_users.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                referral_count INTEGER DEFAULT 0,
                can_use_bot INTEGER DEFAULT 0,
                joined_date TEXT,
                FOREIGN KEY (referred_by) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                referral_date TEXT,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_referral_code(self, user_id):
        hash_input = f"{user_id}{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()
    
    def add_user(self, user_id, username, first_name, referred_by_code=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            conn.close()
            return False
        
        referral_code = self.generate_referral_code(user_id)
        referred_by_id = None
        
        if referred_by_code:
            cursor.execute('SELECT user_id FROM users WHERE referral_code = ?', (referred_by_code,))
            result = cursor.fetchone()
            if result:
                referred_by_id = result[0]
        
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, referral_code, referred_by, joined_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, referral_code, referred_by_id, datetime.now().isoformat()))
        
        if referred_by_id:
            cursor.execute('''
                INSERT INTO referrals (referrer_id, referred_id, referral_date)
                VALUES (?, ?, ?)
            ''', (referred_by_id, user_id, datetime.now().isoformat()))
            
            cursor.execute('''
                UPDATE users SET referral_count = referral_count + 1
                WHERE user_id = ?
            ''', (referred_by_id,))
            
            cursor.execute('SELECT referral_count FROM users WHERE user_id = ?', (referred_by_id,))
            count = cursor.fetchone()[0]
            if count >= 3:
                cursor.execute('UPDATE users SET can_use_bot = 1 WHERE user_id = ?', (referred_by_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def can_use_bot(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT can_use_bot FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def get_referral_code(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT referral_code FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_referral_count(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT referral_count FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def is_admin(self, username):
        return username == "LapsusVishal"
    
    def can_bypass_referral(self, username):
        bypass_users = ["LapsusVishal", "Ghost_oppp"]
        return username in bypass_users if username else False
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results]

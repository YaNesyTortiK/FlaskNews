import sqlite3 as sql
from datetime import datetime
import pytz
from json import load
import os.path

class DbHandler:
    def __init__(self, db_path: str, admins_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Data Base file ({db_path}) not found!")
        if not os.path.exists(admins_path):
            raise FileNotFoundError(f"Admins list file ({admins_path}) not found!")
        self.__db_path = db_path
        self.create_users_table()
        self.create_news_table()
        self.create_categories_table()
        self.create_comments_table()
        with open(admins_path, 'r', encoding='utf-8') as f1:
            self.admins = load(f1)

    def create_users_table(self):
        with sql.connect(self.__db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL UNIQUE
                );
            """)
    
    def add_user(self, email: str, password: str, name: str):
        query = 'INSERT INTO user (email, password, name) values(?, ?, ?)'
        with sql.connect(self.__db_path) as con:
            try:
                con.execute(query, (email, password, name))
            except sql.IntegrityError:
                raise FileExistsError("Login taken")
            
    def del_user(self, email: str):
        query = 'DELETE FROM user WHERE email=?'
        with sql.connect(self.__db_path) as con:
            con.execute(query, (email, ))
        
    def check_password(self, email: str, password: str):
        with sql.connect(self.__db_path) as con:
            data = con.execute(f"SELECT password FROM user WHERE email = '{email}'").fetchone()
            if data[0] == password:
                return True
            else:
                return False
    
    def is_user(self, email: str):
        with sql.connect(self.__db_path) as con:
            return con.execute(f"SELECT * FROM user WHERE email = '{email}'").fetchone()

    def create_news_table(self):
        with sql.connect(self.__db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    author TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    image TEXT,
                    preview TEXT NOT NULL,
                    text TEXT NOT NULL
                );
            """)
    
    def get_news_list(self, byrange: tuple, category: str = None, author: str = None):
        if category == None and author == None:
            query = f"SELECT * FROM news ORDER BY id DESC{f' LIMIT {byrange[1]-byrange[0]} OFFSET {byrange[0]}' if byrange[1] != -1 else ''}"
        elif category != None and author == None:
            query = f"SELECT * FROM news WHERE category=\"{category}\" ORDER BY id DESC{f' LIMIT {byrange[1]-byrange[0]} OFFSET {byrange[0]}' if byrange[1] != -1 else ''}"
        elif category == None and author != None:
            query = f"SELECT * FROM news WHERE author=\"{author}\" ORDER BY id DESC{f' LIMIT {byrange[1]-byrange[0]} OFFSET {byrange[0]}' if byrange[1] != -1 else ''}"
        elif category != None and author != None:
            query = f"SELECT * FROM news WHERE author=\"{author}\" AND category=\"{category}\" ORDER BY id DESC{f' LIMIT {byrange[1]-byrange[0]} OFFSET {byrange[0]}' if byrange[1] != -1 else ''}"
        with sql.connect(self.__db_path) as con:
            return con.execute(query).fetchall()
        
    def add_article(self, title: str, author: str, category: str, text: str, image: str = None, preview: str = None, created_at: str = None):
        if preview == None:
            preview = text[:197]+"..."
        if created_at == None:
            created_at = datetime.now(tz=pytz.timezone('Europe/Moscow')).strftime("%d-%m-%Y %H:%M")
        query = f"INSERT INTO news (title, category, author, created_at, image, preview, text) values(?, ?, ?, ?, ?, ?, ?)"
        with sql.connect(self.__db_path) as con:
            con.execute(query, (title, category, author, created_at, image, preview, text))
    
    def del_article(self, id: int):
        with sql.connect(self.__db_path) as con:
            con.execute(f"DELETE FROM news WHERE id={id}")

    def get_article_data(self, article_id: int):
        with sql.connect(self.__db_path) as con:
            return con.execute(f"SELECT * FROM news WHERE id={article_id}").fetchone()

    def create_categories_table(self):
        with sql.connect(self.__db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    href TEXT PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL
                );
            """)
    
    def get_categories_list(self):
        with sql.connect(self.__db_path) as con:
            return con.execute("SELECT * FROM categories").fetchall()
    
    def add_category(self, href: str, name: str):
        query = f"INSERT INTO categories (href, name) values(?, ?)"
        with sql.connect(self.__db_path) as con:
            con.execute(query, (href, name))
    
    def del_category(self, href: str):
        with sql.connect(self.__db_path) as con:
            return con.execute(f"DELETE FROM categories WHERE href=\"{href}\"").fetchall()
    
    def is_category(self, href: str):
        with sql.connect(self.__db_path) as con:
            data = con.execute(f"SELECT * FROM categories WHERE href=\"{href}\"").fetchone()
            if data == None:
                return False
            else:
                return True
    
    def create_comments_table(self):
        with sql.connect(self.__db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
    
    def get_comments(self, article_id: int):
        query = "SELECT * FROM comments WHERE article_id=?"
        with sql.connect(self.__db_path) as con:
            return con.execute(query, (article_id, )).fetchall()

    def get_comment_by_id(self, article_id: int, comment_id: int):
        query = "SELECT * FROM comments WHERE article_id=? AND id=?"
        with sql.connect(self.__db_path) as con:
            return con.execute(query, (article_id, comment_id)).fetchone()

    def add_comment(self, article_id: int, author: str, text: str, created_at: str = None):
        if created_at == None:
            created_at = datetime.now(tz=pytz.timezone('Europe/Moscow')).strftime("%d-%m-%Y %H:%M")
        query = "INSERT INTO comments (article_id, author, text, created_at) values(?, ?, ?, ?)"
        with sql.connect(self.__db_path) as con:
            con.execute(query, (article_id, author, text, created_at))
        
    def del_comment(self, comment_id: int):
        query = "DELETE FROM comments WHERE id=?"
        with sql.connect(self.__db_path) as con:
            con.execute(query, (comment_id, ))

    def is_admin(self, email: str):
        if email in self.admins:
            return True
        else:
            return False

from flask import g
import sqlite3
import os


def connect_db():
    sql = sqlite3.connect(os.path.join(os.path.dirname(__name__), os.path.abspath('question.db')))
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

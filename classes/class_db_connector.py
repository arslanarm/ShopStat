import sqlite3
from datetime import datetime


class DBConnector:
    def __init__(self, db='stat_database.db'):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

    def insert_job(self, job):
        query = "INSERT INTO videos (`in`, `out`, `date`) VALUES (?, ?, ?)"

        # execute the query with the values
        self.cursor.execute(query, (job['in'], job['out'], datetime.now()))
        self.conn.commit()

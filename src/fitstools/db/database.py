import contextlib
import sqlite3


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self._init_schema()

    def close(self):
        self.c.close()
        self.conn.close()

    def execute(self, sql, *params) -> sqlite3.Cursor:
        self.c.execute(sql, params)
        return self.c

    def _init_schema(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS schema_versions(
                name VARCHAR PRIMARY KEY,
                version INT
            );
        """)


class DatabaseManager:

    @staticmethod
    @contextlib.contextmanager
    def open(file) -> Database:
        db = Database(file)
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def print_version_info():
        import sys
        print("python version %s" % sys.version)
        print("module version %s" % sqlite3.version)
        print("sqlite version %s" % sqlite3.sqlite_version)

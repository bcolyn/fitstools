import contextlib
import sqlite3

from fitstools.db.model import *


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


class RootsDao:

    def __init__(self, db: Database):
        self.db = db
        self._init_schema()

    def _init_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS library_roots (
                id INTEGER PRIMARY KEY,
                name VARCHAR UNIQUE NOT NULL,
                path VARCHAR UNIQUE NOT NULL
            );
        """)
        self.db.execute("INSERT INTO schema_versions (name, version) VALUES ('roots', 1)")

    def list_roots(self):
        rows = self.db.execute("SELECT id, name, path FROM library_roots").fetchall()
        return [Root(**row) for row in rows]

    def get_root_by_name(self, name):
        row = self.db.execute("SELECT id, name, path FROM library_roots WHERE name=?", name).fetchone()
        return Root(**row)

    def put_root(self, root: Root):
        if getattr(root, 'id', 0) == 0:
            cursor = self.db.execute("INSERT INTO library_roots (name, path) VALUES (?, ?)", root.name, root.path)
            root.id = cursor.lastrowid
        else:
            self.db.execute("UPDATE library_roots set name=?, path=? WHERE id=?", root.name, root.path, root.id)
        return root


class FilesDao:

    def __init__(self, db: Database):
        self.db = db
        self._init_schema()

    def _init_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS library_files (
                id INT PRIMARY KEY,
                root INTEGER NOT NULL,
                path VARCHAR NOT NULL,
                content_id BLOB, 
                FOREIGN KEY(root) REFERENCES library_roots(id)
            );            
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS library_files_content_id_idx ON library_files(content_id);")
        self.db.execute("INSERT INTO schema_versions (name, version) VALUES ('files', 1)")

    def find_by_content_id(self):
        pass

    def put_file(self, file):
        if getattr(file, 'id', 0) == 0:
            cursor = self.db.execute("INSERT INTO library_files (root, path) VALUES (?, ?)", file.root.id, file.path)
            file.id = cursor.lastrowid
        else:
            self.db.execute("UPDATE library_files set root=?, path=? WHERE id=?", file.name, file.path, file.id)
        return file

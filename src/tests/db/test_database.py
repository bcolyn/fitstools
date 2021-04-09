from fitstools.db.database import *
from fitstools.db.model import *

from fitstools.db.database import DatabaseManager

temp_file = ":memory:"


def test_db_info():
    DatabaseManager.print_version_info()


def test_db_open():
    with DatabaseManager.open(temp_file) as db:
        res = db.execute("SELECT name FROM sqlite_master")
        name = res.fetchone()
        assert name[0] == "schema_versions"


def test_files_create_schema():
    with DatabaseManager.open(temp_file) as db:
        RootsDao(db)
        res = db.execute("SELECT name FROM sqlite_master WHERE type ='table'")
        tables = [item for t in res for item in t]
        assert "library_roots" in tables


def test_files_root_crud():
    with DatabaseManager.open(temp_file) as db:
        roots = RootsDao(db)
        root = Root(name="main", path=r"C:\Astro")
        roots.put_root(root)
        assert root.id == 1
        new_root = roots.get_root_by_name("main")
        assert new_root.id == 1
        new_root.path = r"D:\Astro"
        roots.put_root(new_root)
        root = roots.get_root_by_name("main")
        assert root.path == r"D:\Astro"
        roots = roots.list_roots()
        assert root in roots


def test_files_file_crud():
    with DatabaseManager.open(temp_file) as db:
        roots = RootsDao(db)
        files = FilesDao(db)
        root = Root(name="main", path=r"C:\Astro")
        roots.put_root(root)
        file = File(root=root, path=r"Deep Sky\Raw\filename.fit")
        files.put_file(file)

import os
import typing
from typing import List

import fs.path
from fs.base import FS
from fs.info import Info
from logzero import logger
from peewee import Database, SqliteDatabase, Query

from fitstools.db.database_peewee import Root, File, Image


def explain_query_plan(query: Query):
    sql, params = query.sql()

    # To get the query plan:
    curs = Root._meta.database.execute_sql('EXPLAIN QUERY PLAN ' + sql, params)
    print(curs.fetchall())  # prints query plan


class DataStorage:
    db: typing.Optional[Database]
    _CORE_MODELS = [Root, File, Image]

    def __init__(self):
        pass

    def open(self, db_file):
        self.db = SqliteDatabase(db_file)
        self.db.bind(self._CORE_MODELS, bind_refs=False, bind_backrefs=False)
        self.db.connect()
        self.db.create_tables(self._CORE_MODELS)

    def close(self):
        self.db.close()
        self.db = None


class Importer:

    def _import_file(self, file: Info, rel_path, root):
        logger.debug("[root %s] record file stats: %s/%s", root.name, rel_path, file.name)
        mtime_millis = int(file.modified.timestamp() * 1000)
        db_file = File.select(File.size, File.mtime_millis).where(File.root == root, File.path == rel_path,
                                                                  File.name == file.name).get_or_none()
        if db_file is None:
            File.create(name=file.name, path=rel_path, root=root, size=file.size, mtime_millis=mtime_millis)
        else:
            if db_file.mtime_millis != mtime_millis or db_file.size != file.size:
                (File
                 .insert(name=file.name, path=rel_path, root=root, size=file.size, mtime_millis=mtime_millis)
                 .on_conflict('replace')
                 .execute())
            else:
                logger.debug("%s has not changed", file.name)

    @staticmethod
    def marked_bad(f: Info) -> bool:
        """" skips over files that are marked bad """
        filename = f.name
        return filename.lower().startswith("bad")

    @staticmethod
    def is_fits(f: Info) -> bool:
        filename = f.name
        if Importer.is_compressed(f):
            filename = os.path.splitext(filename)[0]
        return filename.lower().endswith(".fit") or filename.lower().endswith(".fits")

    @staticmethod
    def is_compressed(f: Info) -> bool:
        filename = f.name
        return filename.lower().endswith(".xz") or filename.lower().endswith(".gz")

    @staticmethod
    def _file_filter(x: Info):
        return Importer.is_fits(x) and not Importer.marked_bad(x)

    @staticmethod
    def _dir_filter(x: Info):
        return not Importer.marked_bad(x)

    def import_files(self):
        roots: typing.Sequence[Root] = list(Root.select().execute())
        for root in roots:
            logger.debug("import library root: %s", str(root.last_path))
            self.import_files_from(fs.open_fs(root.last_path), root)

    # TODO: check root exists and is non-empty
    def import_files_from(self, root_fs: FS, root: Root):
        dir_queue: List[str] = ['.']
        while len(dir_queue) > 0:
            current_dir: str = dir_queue.pop()
            filtered_files = set()
            entry: Info
            for entry in root_fs.scandir(current_dir, namespaces=['details']):
                if entry.is_dir:
                    if self._dir_filter(entry):
                        dir_queue.append(fs.path.join(current_dir, entry.name))
                    else:
                        pass  # TODO: log skipping
                if entry.is_file:
                    if self._file_filter(entry):
                        self._import_file(entry, current_dir, root)
                        filtered_files.add(entry.name)
                    else:
                        pass  # TODO: log skipping

            # evict deleted files
            query = File.select(File.rowid, File.name).where(File.root == root, File.path == current_dir)
            for (id, name) in query.tuples():
                if name not in filtered_files:
                    File.delete_by_id(id)

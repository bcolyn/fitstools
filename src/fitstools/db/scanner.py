import os
import typing
from typing import List

import fs.path
from fs.base import FS
from fs.info import Info
from logzero import logger
from peewee import Database, SqliteDatabase, Query

from fitstools.db.database_peewee import Root, File, CORE_MODELS


def explain_query_plan(query: Query):
    sql, params = query.sql()

    # To get the query plan:
    curs = Root._meta.database.execute_sql('EXPLAIN QUERY PLAN ' + sql, params)
    print(curs.fetchall())  # prints query plan


class DataStorage:
    db: typing.Optional[Database]

    def __init__(self):
        pass

    def open(self, db_file):
        self.db = SqliteDatabase(db_file, pragmas={
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,  # 64MB
            'foreign_keys': 1,
            'application_id': 0x46495453,  # FITS
            'user_version': 1
        })
        self.db.bind(CORE_MODELS, bind_refs=False, bind_backrefs=False)
        self.db.connect()
        self.db.create_tables(CORE_MODELS)

    def close(self):
        self.db.close()
        self.db = None

    def begin_tx(self):
        self.db.atomic()

    def commit_tx(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()


class ChangeList:
    def __init__(self):
        self.new_files = list()
        self.removed_files = list()
        self.changed_ids = list()
        self.changed_files = list()

    def apply_all(self):
        File.bulk_create(self.new_files, batch_size=100)
        for file in self.removed_files:
            File.delete_by_id(file.rowid)
        for id in self.changed_ids:  # delete and re-create
            File.delete_by_id(id)
        File.bulk_create(self.changed_files, batch_size=100)


class Importer:
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
            logger.info("import library root: %s", str(root.last_path))
            change_list = self.import_files_from(fs.open_fs(root.last_path), root)
            yield change_list

    # TODO: check root exists and is non-empty
    def import_files_from(self, root_fs: FS, root: Root) -> ChangeList:
        dir_queue: List[str] = ['.']
        all_dirs = set(dir_queue)
        result = ChangeList()
        while len(dir_queue) > 0:
            current_dir: str = dir_queue.pop()
            filtered_files = set()
            entry: Info
            for entry in root_fs.scandir(current_dir, namespaces=['details']):
                if entry.is_dir:
                    if self._dir_filter(entry):
                        dir_path = fs.path.join(current_dir, entry.name)
                        dir_queue.append(dir_path)
                        all_dirs.add(dir_path)
                    else:
                        pass  # TODO: log skipping
                if entry.is_file:
                    if self._file_filter(entry):
                        self._import_file(entry, current_dir, root, result)
                        filtered_files.add(entry.name)
                    else:
                        pass  # TODO: log skipping

            # evict deleted files
            query = File.select(File.rowid, File.name).where(File.root == root, File.path == current_dir)
            for file in query.execute():
                if file.name not in filtered_files:
                    result.removed_files.append(file)

        # clean up deleted dirs
        query = File.select(File.path).distinct().where(File.root == root)
        for (old_path,) in query.tuples().iterator():
            if old_path not in all_dirs:
                files = File.select().where(File.root == root, File.path == old_path).execute()
                for file in files:
                    result.removed_files.append(file)

        return result

    def _import_file(self, file: Info, rel_path, root, changelist):
        logger.debug("[root %s] record file stats: %s/%s", root.name, rel_path, file.name)

        mtime_millis = int(file.modified.timestamp() * 1000)

        db_file = File.select(File.rowid, File.size, File.mtime_millis) \
            .where(File.root == root, File.path == rel_path, File.name == file.name).get_or_none()
        if db_file is None:
            model = File(name=file.name, path=rel_path, root=root, size=file.size, mtime_millis=mtime_millis)
            changelist.new_files.append(model)
        else:
            if db_file.mtime_millis != mtime_millis or db_file.size != file.size:
                model = File(name=file.name, path=rel_path, root=root, size=file.size, mtime_millis=mtime_millis)
                changelist.changed_ids.append(db_file.rowid)
                changelist.changed_files.append(model)

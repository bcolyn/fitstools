#!/usr/bin/env python3
import os
import typing
from pathlib import Path

from logzero import logger
from peewee import *

from fitstools.db.database_peewee import File, Root, Image
from fitstools.util import gather_files, is_fits, marked_bad


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

    def load_roots(self):
        return list(Root.select().execute())

    def add_root(self, insert):
        return self.db.execute(insert)

    def record_file_stats(self, file: os.DirEntry, rel_path: Path, root: Root):
        logger.debug("[root %s] record file stats: %s/%s", root.name, rel_path, str(file.name))
        stat = file.stat()
        mtime_millis = stat.st_mtime_ns // 1_000_000
        File.create(name=file.name, path=rel_path, root=root, size=stat.st_size, mtime_millis=mtime_millis)


class Importer:
    storage: DataStorage

    def __init__(self, storage: DataStorage):
        self.storage = storage

    def _process_files(self, files: typing.Sequence[os.DirEntry], parent: os.DirEntry, root: Root):
        file: os.DirEntry
        from pathlib import Path
        rel_path = Path(parent.path).relative_to(Path(root.last_path))
        # all files assumed to be in same directory
        for file in files:
            self._import_file(file, rel_path, root)

    def import_files(self):
        roots: typing.Sequence[Root] = self.storage.load_roots()
        for root in roots:
            logger.debug("import library root: %s", str(root.last_path))
            # TODO: check root exists and is non-empty
            gather_files(cb=lambda files, parent: self._process_files(files, parent, root),
                         start=root.last_path,
                         file_filter=lambda x: is_fits(x) and not marked_bad(x),
                         dir_filter=lambda x: not marked_bad(x))

    def _import_file(self, file: os.DirEntry, rel_path: Path, root):
        self.storage.record_file_stats(file, rel_path, root)


def main():
    import logging
    logger = logging.getLogger('peewee')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    root_path = r"Z:\Deep Sky\Raw\ZWO_ASI183MC\2019-11-20"
    database = ":memory:"

    data_storage = DataStorage()
    data_storage.open(database)
    Root.create(last_path=root_path, name="test_root")
    try:
        importer = Importer(data_storage)
        importer.import_files()
    finally:
        data_storage.close()


if __name__ == "__main__":
    main()

import logging

from fitstools.db.database_peewee import *
from fitstools.db.scanner import Importer

NUM_FILES = 6  # 8 images, 2 bad, 1 csv ignored

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def initial_import(filesystem):
    root = Root(name="dummy", last_path=r'C:\TEMP')
    root.save()
    importer = Importer()
    importer.import_files_from(filesystem, root)
    return root, importer


def test_fixture(filesystem):
    for path, dirs, files in filesystem.walk("/", namespaces=['details']):
        print("[%s] %d subdirs %d files" % (path, len(dirs), len(files)))


def test_initial_import(filesystem, database):
    initial_import(filesystem)
    assert File.select().count() == NUM_FILES


def test_reimport(filesystem, database):
    (root, importer) = initial_import(filesystem)
    importer.import_files_from(filesystem, root)
    assert File.select().count() == NUM_FILES


def test_delete_file(filesystem, database):
    (root, importer) = initial_import(filesystem)

    filesystem.remove("image01.fits")
    importer.import_files_from(filesystem, root)
    assert File.select().count() == NUM_FILES - 1

    filesystem.remove("test/2021-12-26/Darks/image06.fits")
    importer.import_files_from(filesystem, root)
    assert File.select().count() == NUM_FILES - 2


def test_delete_dirs(filesystem, database):
    (root, importer) = initial_import(filesystem)
    filesystem.removetree("test/2021-12-25")
    importer.import_files_from(filesystem, root)
    assert File.select().count() == 2
    # TODO: check deleted directories


def test_changed_file(filesystem, database):
    (root, importer) = initial_import(filesystem)
    filesystem.touch("test/2021-12-26/Darks/image06.fits")
    importer.import_files_from(filesystem, root)
    assert File.select().count() == NUM_FILES
    # TODO: check deleted metas

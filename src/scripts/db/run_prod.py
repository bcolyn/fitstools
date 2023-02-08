#!/usr/bin/env python3

import reset_db
import update_files
import group_sets
import extract_metadata

if __name__ == "__main__":
    database = "prod.db"
    reset_db.main(database, r'Z:\Deep Sky\Raw')
    update_files.main(database)
    extract_metadata.main(database)
    group_sets.main(database)

#!/usr/bin/env python3

import reset_db
import update_files
import group_sets
import extract_metadata

if __name__ == "__main__":
    database = "test_min.db"
    reset_db.main(database)
    update_files.main(database)
    extract_metadata.main(database)
    group_sets.main(database)

#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Remove bad subs, based on SubFrameSelector CSV')
    parser.add_argument('--action', '-a', default='skip', choices=['rename', 'delete'])
    parser.add_argument('csvfile')
    args = parser.parse_args()
    process_csv(args.csvfile, args.action)


def process_csv(file, action):
    print("Loading file ", file, "[", action, " mode ]")
    with open(file, newline="") as infile:
        reader = csv.reader(infile)
        header = []
        for row in reader:
            if header == [] and row[0] != 'Index':
                continue  # skip over the first lines with metadata
            if header == [] and row[0] == 'Index':
                header = row  # store the header line
                continue
            # data item
            dict_row = dict(zip(header, row))
            process_sub(dict_row, action)


def process_sub(dict_row, action):
    approved = dict_row['Approved']
    file = dict_row["File"]
    if approved == 'false':
        if action == 'rename':
            rename_sub(file)
        elif action == 'delete':
            delete_sub(file)
        else:
            print(action, file)


def rename_sub(file):
    path = Path(file)
    if not path.name.startswith("BAD"):
        targetname = "BAD_" + path.name
        targetpath = Path(path.parent, targetname)
        if path.exists():
            print('renaming', path)
            os.rename(path, targetpath)
        else:
            print('not found', path)


def delete_sub(file):
    path = Path(file)
    if path.exists():
        print('deleting', path)
        os.remove(path)
    else:
        print('not found', path)


if __name__ == "__main__":
    main()

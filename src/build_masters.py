#!/usr/bin/env python3
from os import DirEntry

from fitstools.util import walk_dir, sha1sum, is_master
from fitstools.cli import Config, BaseReporter

import os
import functools


class Reporter(BaseReporter):

    def __init__(self):
        super().__init__()
        self.__count = 0

    def report_master(self):
        self.dot()
        self.__count += 1

    def report(self):
        print("done")
        print("master files indexed:", self.__count)


def process_file(pdir, output, reporter: Reporter, file: DirEntry):
    rel_path = os.path.relpath(file.path, pdir)
    if is_master(file.name):
        reporter.report_master()
        hex_sum = sha1sum(file)
        output.write(hex_sum + " *" + rel_path + "\n")


def main():
    """ Main entry point of the app """
    conf = Config()
    reporter = Reporter()
    pdir = os.path.dirname(conf.data.masters.sha1sum_file)
    with open(conf.data.masters.sha1sum_file, "w+") as output:
        for p in conf.data.masters.dirs:
            walk_dir(functools.partial(process_file, pdir, output, reporter), p)
    reporter.report()


if __name__ == "__main__":
    main()

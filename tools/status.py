#!/usr/bin/env python3

from __future__ import print_function, unicode_literals
from subprocess import Popen, PIPE
from sys import exit
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()


def run(*cmd):
    process = Popen(cmd, stdout=PIPE)
    output, err = process.communicate()
    if process.wait():
        exit(1)
    return output.strip().decode()


def main():
    sha = run("git", "rev-parse", "HEAD")
    print("STABLE_scm_hash", sha)

    dirty = run("git", "status", "--porcelain")

    scs = run("git", "log", "--pretty=%h")
    print("STABLE_scm_shortcleanhash", "-" if dirty else scs)

    date_commit = run("git", "log", "--pretty=%ct")
    date_now = str(int(datetime.timestamp(datetime.now())))
    date_now = date_commit
    print("STABLE_change_timestamp", date_now if dirty else date_commit)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import print_function, unicode_literals
from subprocess import Popen, PIPE
from sys import exit
from datetime import datetime

# Use bazel flag --workspace_status_command=./tools/status.py to
# include stamp data.


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

    scs = run("git", "log", "-1", "--pretty=%h")
    print("STABLE_scm_shortcleanhash", "-" if dirty else scs)

    # Timestamp is date of commit unless the repo is dirty
    date_commit = run("git", "log", "-1", "--pretty=%ct")
    date_now = str(int(datetime.timestamp(datetime.now())))
    print("STABLE_change_timestamp", date_now if dirty else date_commit)


if __name__ == "__main__":
    main()

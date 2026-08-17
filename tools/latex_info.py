from absl import app
from absl import flags
import os
import datetime

FLAGS = flags.FLAGS
flags.DEFINE_string('content', '', 'path to LaTeX file with recipe content')
flags.DEFINE_string('info', '', 'info file')

flags.DEFINE_string('stablestatus', 'bazel-out/stable-status.txt', 'file')
flags.DEFINE_string('volatilestatus', 'bazel-out/volatile-status.txt', 'file')

# Populate latex macros from the stable-status.txt and volatile-status.txt


def status_line(s):
    return [*s.strip().split(maxsplit=1), ""][0:2]


def main(argv):
    stablestatus = dict(
        status_line(s) for s in open(FLAGS.stablestatus).readlines())
    volatilestatus = dict(
        status_line(s) for s in open(FLAGS.volatilestatus).readlines())

    change_timestamp = stablestatus.get("STABLE_change_timestamp")
    date1 = (
        datetime.datetime.fromtimestamp(int(change_timestamp))
        if change_timestamp else datetime.datetime.now())
    print(f"\\year={date1.year}\\month={date1.month}\\day={date1.day}")
    print(
        f"\\newcommand{{\\scmhash}}{{{stablestatus.get('STABLE_scm_shortcleanhash', '')}}}"
    )


if __name__ == '__main__':
    app.run(main)

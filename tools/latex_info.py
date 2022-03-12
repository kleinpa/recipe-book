from absl import app
from absl import flags
import jinja2
import os
import datetime

FLAGS = flags.FLAGS
flags.DEFINE_string('content', '', 'path to LaTeX file with recipe content')
flags.DEFINE_string('template', 'single.tex.jinja2', 'Template file')
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

    date1 = datetime.datetime.fromtimestamp(
        int(stablestatus["STABLE_change_timestamp"]))
    print(f"\\year={date1.year}\\month={date1.month}\\day={date1.day}")
    print(
        f"\\newcommand{{\\scmhash}}{{{stablestatus['STABLE_scm_shortcleanhash']}}}"
    )


if __name__ == '__main__':
    app.run(main)

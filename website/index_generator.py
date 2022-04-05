from absl import app
from absl import flags
import jinja2
import os
import datetime

FLAGS = flags.FLAGS
flags.DEFINE_string('template', 'index.html.jinja2', 'Template file')
flags.DEFINE_string('stablestatus', 'bazel-out/stable-status.txt', 'file')
flags.DEFINE_string('volatilestatus', 'bazel-out/volatile-status.txt', 'file')


def status_line(s):
    return [*s.strip().split(maxsplit=1), ""][0:2]


def main(argv):
    context = dict()

    stablestatus = dict(
        status_line(s) for s in open(FLAGS.stablestatus).readlines())
    volatilestatus = dict(
        status_line(s) for s in open(FLAGS.volatilestatus).readlines())

    context["recipes"] = []
    for f in argv[1:]:
        context["recipes"].append({
            "name": os.path.basename(f),
            "url": os.path.basename(f),
        })

    context["title"] = "Recipes"
    context["version"] = stablestatus["STABLE_scm_shortcleanhash"]
    context["date"] = datetime.datetime.fromtimestamp(
        int(stablestatus["STABLE_change_timestamp"]))

    with open(os.path.join(os.path.dirname(__file__), FLAGS.template)) as f:
        template = jinja2.Template(f.read())
        print(template.render(context))


if __name__ == '__main__':
    app.run(main)

from absl import app
from absl import flags
import jinja2
import os

FLAGS = flags.FLAGS
flags.DEFINE_string('content', '', 'path to LaTeX file with recipe content')
flags.DEFINE_string('template', 'single.tex.jinja2', 'Template file')


def main(argv):
    with open(os.path.join(os.path.dirname(__file__),
                           FLAGS.template)) as file_:
        template = jinja2.Template(file_.read())
    print(template.render(include_path=FLAGS.content.replace('.tex', '')))


if __name__ == '__main__':
    app.run(main)

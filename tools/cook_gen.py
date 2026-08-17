"""Render a .cook recipe file to all output formats in a single invocation.

Parses the .cook file once and writes whichever of --tex/--html/--manifest
are requested, reusing the renderers in cook_to_latex.py/cook_to_html.py.
"""

import json
import os

from absl import app
from absl import flags

from tools import cook_common
from tools import cook_to_html
from tools import cook_to_latex

FLAGS = flags.FLAGS
flags.DEFINE_string('input', None, 'path to a .cook recipe file')
flags.DEFINE_string('tex', None, 'path to write the generated .tex to')
flags.DEFINE_string('html', None, 'path to write the generated .html to')
flags.DEFINE_string('manifest', None, 'path to write the JSON manifest to')
flags.mark_flag_as_required('input')


def main(argv):
    del argv
    recipe = cook_common.parse_file(FLAGS.input)

    if FLAGS.tex:
        with open(FLAGS.tex, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cook_to_latex.render(recipe))

    if FLAGS.html:
        # cook.bzl always writes the html to "{name}/index.html" and the
        # matching single_pages PDF is packaged as the sibling "{name}.pdf"
        # (see website/BUILD.bazel's pkg_tar), so the relative link back to
        # it can be derived from the output path itself.
        name = os.path.basename(os.path.dirname(FLAGS.html))
        pdf_url = f'../{name}.pdf'
        with open(FLAGS.html, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cook_to_html.render(recipe, pdf_url=pdf_url))

    if FLAGS.manifest:
        with open(FLAGS.manifest, 'w', encoding='utf-8') as f:
            json.dump({'title': recipe.title, 'part': recipe.part}, f)


if __name__ == '__main__':
    app.run(main)

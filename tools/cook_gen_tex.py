"""Render a .cook recipe file to LaTeX.

Pure rendering logic lives in cook_to_latex.py; this is its CLI entry point.
Kept as its own binary (separate from cook_gen_html.py) so that a change to
the HTML renderer doesn't invalidate the tex-generating build action --
the downstream LaTeX/PDF build is slow, so it shouldn't rebuild for
html-only changes.
"""

from absl import app
from absl import flags

from tools import cook_common
from tools import cook_to_latex

FLAGS = flags.FLAGS
flags.DEFINE_string('input', None, 'path to a .cook recipe file')
flags.DEFINE_string('tex', None, 'path to write the generated .tex to')
flags.mark_flag_as_required('input')
flags.mark_flag_as_required('tex')


def main(argv):
    del argv
    recipe = cook_common.parse_file(FLAGS.input)
    with open(FLAGS.tex, 'w', encoding='utf-8', newline='\n') as f:
        f.write(cook_to_latex.render(recipe))


if __name__ == '__main__':
    app.run(main)

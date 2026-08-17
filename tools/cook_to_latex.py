"""Renders a parsed .cook Recipe to the LaTeX macros defined in common.tex.

Pure rendering logic, no CLI -- see cook_gen.py for the command-line tool.
"""

import re

from tools import cook_common

_DIMENSION_RE = re.compile(r'^\d+(\.\d+)?\s*x\s*\d+(\.\d+)?$')

_LATEX_SPECIAL = {
    '\\': r'\textbackslash{}',
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
}


def latex_escape(text):
    return ''.join(_LATEX_SPECIAL.get(ch, ch) for ch in text)


def render_run(run):
    if isinstance(run, cook_common.Text):
        return latex_escape(run.text)
    if isinstance(run, cook_common.Footnote):
        return f'\\footnote{{{latex_escape(run.text)}}}'
    if isinstance(run, cook_common.InlineQuantity):
        if run.unit == '' and _DIMENSION_RE.match(run.value):
            return f'\\SI[product-units = single]{{{run.value}}}{{}}'
        return f'\\SI{{{run.value}}}{{{run.unit}}}'
    raise TypeError(run)


def render_prose(block):
    return ''.join(render_run(r) for r in block.runs)


def render_ingredient(item):
    name = latex_escape(item.name)
    a = item.amount
    if a.alt_value is not None:
        return f'\\ingredientAlt{{{a.value}}}{{{a.unit}}}{{{a.alt_value}}}{{{a.alt_unit}}}{{{name}}}'
    return f'\\ingredient{{{a.value}}}{{{a.unit}}}{{{name}}}'


def render_block(block):
    if isinstance(block, cook_common.ProseBlock):
        return render_prose(block)
    lines = [render_ingredient(item) for item in block.items]
    return '\\begin{ingredients}\n' + '\n'.join(lines) + '\n\\end{ingredients}'


def render(recipe):
    chunks = [f'\\recipe{{{latex_escape(recipe.title)}}}']
    for block in recipe.intro:
        chunks.append(render_block(block))
    for section in recipe.sections:
        chunks.append(f'\\recipesection{{{latex_escape(section.name)}}}')
        for block in section.blocks:
            chunks.append(render_block(block))
    return '\n\n'.join(chunks) + '\n'

"""Renders a parsed .cook Recipe to a standalone HTML page.

Pure rendering logic, no CLI -- see cook_gen.py for the command-line tool.
"""

import html
import re

from tools import cook_common

_DIMENSION_RE = re.compile(r'^\d+(\.\d+)?\s*x\s*\d+(\.\d+)?$')

_STYLE = """
:root { color-scheme: light; }
body {
  max-width: 38em;
  margin: 2.5em auto;
  padding: 0 1.25em;
  background: #fff;
  color: #000;
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.5;
}
h1 { font-size: 1.6em; margin-bottom: 0.2em; }
h2 { font-size: 1.1em; margin-top: 1.6em; }
p { margin: 1em 0; }
table.ingredients {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
  margin: 0.8em 0 1.2em;
}
table.ingredients td { padding: 0.15em 0.8em; vertical-align: top; }
table.ingredients td.amount { width: 11em; text-align: right; white-space: nowrap; border-right: 1px solid #000; }
sup a { text-decoration: none; }
footer { margin-top: 3em; font-size: 0.8em; opacity: 0.5; }
"""


def html_escape(text):
    return html.escape(text, quote=False)


def format_amount(a):
    primary = f'{a.value} {a.unit}'.strip()
    if a.alt_value is not None:
        alt = f'{a.alt_value} {a.alt_unit}'.strip()
        return f'{primary} ({alt})'
    return primary


def format_inline_quantity(value, unit):
    if unit == '' and _DIMENSION_RE.match(value):
        return html_escape(value)
    if unit.startswith('°') or unit == '':
        return html_escape(f'{value}{unit}')
    return html_escape(f'{value} {unit}')


def render_run(run, footnotes):
    if isinstance(run, cook_common.Text):
        return html_escape(run.text)
    if isinstance(run, cook_common.InlineQuantity):
        return f'<strong>{format_inline_quantity(run.value, run.unit)}</strong>'
    if isinstance(run, cook_common.Footnote):
        footnotes.append(run.text)
        n = len(footnotes)
        return f'<sup id="fnref{n}"><a href="#fn{n}">[{n}]</a></sup>'
    raise TypeError(run)


def render_prose(block, footnotes):
    text = ''.join(render_run(r, footnotes) for r in block.runs)
    return f'<p>{text}</p>'


def render_ingredients(block):
    rows = []
    for item in block.items:
        amount = html_escape(format_amount(item.amount))
        name = html_escape(item.name)
        rows.append(
            f'<tr><td class="amount"><strong>{amount}</strong></td>'
            f'<td><strong>{name}</strong></td></tr>'
        )
    return '<table class="ingredients">\n' + '\n'.join(rows) + '\n</table>'


def render_block(block, footnotes):
    if isinstance(block, cook_common.ProseBlock):
        return render_prose(block, footnotes)
    return render_ingredients(block)


def render(recipe, pdf_url=None):
    footnotes = []
    body = []
    for block in recipe.intro:
        body.append(render_block(block, footnotes))
    for section in recipe.sections:
        body.append(f'<h2>{html_escape(section.name)}</h2>')
        for block in section.blocks:
            body.append(render_block(block, footnotes))

    footer_parts = []
    if pdf_url:
        pdf_name = pdf_url.rsplit('/', 1)[-1]
        footer_parts.append(
            f'<p><a href="{html_escape(pdf_url)}">{html_escape(pdf_name)}</a></p>')
    if footnotes:
        items = []
        for n, text in enumerate(footnotes, start=1):
            items.append(
                f'<li id="fn{n}">{html_escape(text)} '
                f'<a href="#fnref{n}">&#8617;</a></li>')
        footer_parts.append('<ol>' + ''.join(items) + '</ol>')
    footer = '<footer>' + ''.join(footer_parts) + '</footer>' if footer_parts else ''

    title = html_escape(recipe.title)
    return (
        '<!doctype html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n'
        f'<style>{_STYLE}</style>\n'
        '</head>\n'
        '<body>\n'
        f'<h1>{title}</h1>\n'
        + '\n'.join(body) + '\n'
        + footer + '\n'
        '</body>\n'
        '</html>\n'
    )

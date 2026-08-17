"""Parser and shared data model for the .cook recipe format.

See recipes/*.cook for examples. Renderers (cook_to_latex.py,
cook_to_html.py) consume the Recipe returned by parse() and are
responsible for their own escaping -- this module only extracts
structure, it never escapes text for a particular output format.
"""

import dataclasses
import re
from typing import List, Optional, Union

_METADATA_RE = re.compile(r'^>>\s*([\w.]+)\s*:\s*(.*)$')
_SECTION_RE = re.compile(r'^=\s+(.+?)\s*$')
_INGREDIENT_RE = re.compile(r'^@(?P<name>[^{]+)\{(?P<spec>[^}]*)\}$')
_RUN_RE = re.compile(r'\[\^(?P<foot>[^\]]*)\]|\{\{(?P<inline>[^}]*)\}\}')


@dataclasses.dataclass
class Amount:
    value: str
    unit: str
    alt_value: Optional[str] = None
    alt_unit: Optional[str] = None


@dataclasses.dataclass
class Ingredient:
    name: str
    amount: Amount


@dataclasses.dataclass
class Text:
    text: str


@dataclasses.dataclass
class InlineQuantity:
    value: str
    unit: str


@dataclasses.dataclass
class Footnote:
    text: str


Run = Union[Text, InlineQuantity, Footnote]


@dataclasses.dataclass
class ProseBlock:
    runs: List[Run]


@dataclasses.dataclass
class IngredientsBlock:
    items: List[Ingredient]


Block = Union[ProseBlock, IngredientsBlock]


@dataclasses.dataclass
class Section:
    name: str
    blocks: List[Block]


@dataclasses.dataclass
class Recipe:
    title: str
    part: Optional[str]
    intro: List[Block]
    sections: List[Section]


def _parse_amount_part(part):
    part = part.strip()
    if '%' in part:
        value, unit = part.split('%', 1)
    else:
        value, unit = part, ''
    return value.strip(), unit.strip()


def _parse_amount(spec):
    primary, _, alt = spec.partition('|')
    value, unit = _parse_amount_part(primary)
    if alt:
        alt_value, alt_unit = _parse_amount_part(alt)
        return Amount(value, unit, alt_value, alt_unit)
    return Amount(value, unit)


def _parse_ingredient_line(line):
    m = _INGREDIENT_RE.match(line)
    if not m:
        raise ValueError(f'malformed ingredient line: {line!r}')
    return Ingredient(m.group('name').strip(), _parse_amount(m.group('spec')))


def _parse_prose(text):
    text = ' '.join(text.split('\n'))
    runs = []
    pos = 0
    for m in _RUN_RE.finditer(text):
        if m.start() > pos:
            runs.append(Text(text[pos:m.start()]))
        if m.group('foot') is not None:
            runs.append(Footnote(m.group('foot')))
        else:
            value, unit = _parse_amount_part(m.group('inline'))
            runs.append(InlineQuantity(value, unit))
        pos = m.end()
    if pos < len(text):
        runs.append(Text(text[pos:]))
    return ProseBlock(runs)


def _parse_block(raw):
    lines = raw.split('\n')
    if all(line.startswith('@') for line in lines):
        return IngredientsBlock([_parse_ingredient_line(l) for l in lines])
    return _parse_prose(raw)


def parse(text):
    lines = text.split('\n')

    i = 0
    title = None
    part = None
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        m = _METADATA_RE.match(line)
        if not m:
            break
        key, value = m.group(1), m.group(2).strip()
        if key == 'title':
            title = value
        elif key == 'part':
            part = value
        i += 1

    if title is None:
        raise ValueError('missing ">> title: ..." metadata')

    body = '\n'.join(lines[i:])
    raw_blocks = [b.strip() for b in re.split(r'\n\s*\n+', body)]
    raw_blocks = [b for b in raw_blocks if b]

    intro = []
    sections = []
    current = None
    for raw in raw_blocks:
        m = _SECTION_RE.match(raw) if '\n' not in raw else None
        if m:
            current = Section(m.group(1), [])
            sections.append(current)
            continue
        block = _parse_block(raw)
        if current is None:
            intro.append(block)
        else:
            current.blocks.append(block)

    return Recipe(title, part, intro, sections)


def parse_file(path):
    with open(path, encoding='utf-8') as f:
        return parse(f.read())

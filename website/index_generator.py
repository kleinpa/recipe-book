from absl import app
from absl import flags
import jinja2
import os
import re
import json
import datetime
from collections import defaultdict

FLAGS = flags.FLAGS
flags.DEFINE_string('template', 'index.html.jinja2', 'Template file')
flags.DEFINE_string('stablestatus', 'bazel-out/stable-status.txt', 'file')
flags.DEFINE_string('volatilestatus', 'bazel-out/volatile-status.txt', 'file')

_DEFAULT_PART = 'Recipes'

_PART_RE = re.compile(r'\\part\{(?P<name>[^}]*)\}')
_INCLUDE_RE = re.compile(r'\\include\{recipes/(?P<slug>[^}]*)\}')


def status_line(s):
    return [*s.strip().split(maxsplit=1), ""][0:2]


def book_order(tex):
    """Returns book.tex's \\part/\\include order as (part_order, {part: [slug, ...]})."""
    part_order = []
    slugs_by_part = defaultdict(list)
    part = _DEFAULT_PART
    for line in tex.splitlines():
        part_match = _PART_RE.search(line)
        include_match = _INCLUDE_RE.search(line)
        if part_match:
            part = part_match.group('name')
            part_order.append(part)
        elif include_match:
            slugs_by_part[part].append(include_match.group('slug'))
    return part_order, slugs_by_part


def main(argv):
    context = dict()

    stablestatus = dict(
        status_line(s) for s in open(FLAGS.stablestatus).readlines())
    volatilestatus = dict(
        status_line(s) for s in open(FLAGS.volatilestatus).readlines())

    recipes = defaultdict(dict)
    part_order, slugs_by_part = [], defaultdict(list)
    for f in argv[1:]:
        name, ext = os.path.splitext(os.path.basename(f))
        if ext == '.json':
            with open(f) as manifest:
                data = json.load(manifest)
            recipes[name]['title'] = data['title']
            recipes[name]['part'] = data.get('part') or _DEFAULT_PART
        elif ext == '.tex':
            with open(f) as book:
                part_order, slugs_by_part = book_order(book.read())
        elif ext == '.pdf':
            context['book_pdf_url'] = os.path.basename(f)

    parts = defaultdict(list)
    for name, recipe in recipes.items():
        parts[recipe.get('part', _DEFAULT_PART)].append({
            'title': recipe.get('title', name),
            'url': name,
        })

    # Recipes/parts not found in book.tex (e.g. a new one still missing
    # its \include) sort alphabetically after the ones book.tex does know
    # about, rather than being silently dropped.
    def slug_rank(part, item):
        slugs = slugs_by_part.get(part, [])
        return (slugs.index(item['url']) if item['url'] in slugs else
                len(slugs), item['title'])

    def part_rank(part):
        return (part_order.index(part) if part in part_order else
                len(part_order), part)

    context['parts'] = [{
        'name': part,
        'recipes': sorted(items, key=lambda item: slug_rank(part, item)),
    } for part, items in sorted(parts.items(), key=lambda kv: part_rank(kv[0]))]

    context["title"] = "Recipes"
    context["version"] = stablestatus.get("STABLE_scm_shortcleanhash", "")
    change_timestamp = stablestatus.get("STABLE_change_timestamp")
    date = (
        datetime.datetime.fromtimestamp(int(change_timestamp))
        if change_timestamp else datetime.datetime.now())
    # %-d (no leading zero) is a glibc/BSD strftime extension, so format
    # the day ourselves instead.
    context["date_str"] = f'{date.strftime("%B")} {date.day}, {date.year}'

    with open(os.path.join(os.path.dirname(__file__), FLAGS.template)) as f:
        template = jinja2.Template(f.read())
        print(template.render(context))


if __name__ == '__main__':
    app.run(main)

"""Сборка статического кабинета для GitHub Pages."""

import argparse
import os
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dsa_lab.content import list_lessons
from dsa_lab.site import normalize_base, template_context


ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
DEFAULT_OUT = ROOT / 'site'


def export_site(destination, base=''):
    dest = Path(destination)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(str(WEB / 'templates')),
        autoescape=select_autoescape(['html', 'xml']),
    )
    context = template_context(base=base, dsa_static=True)
    _write(dest / 'index.html', env.get_template('index.html').render(context))

    for lesson in list_lessons():
        page = dest / 'lessons' / lesson['slug'] / 'index.html'
        page.parent.mkdir(parents=True, exist_ok=True)
        _write(page, env.get_template('lesson.html').render(
            template_context(base=base, dsa_static=True, lesson=lesson),
        ))

    shutil.copytree(WEB / 'static', dest / 'static')
    (dest / '.nojekyll').write_text('', encoding='utf-8')
    _write(dest / '404.html', _not_found_html(normalize_base(base)))
    return dest


def _write(path, html):
    path.write_text(html, encoding='utf-8')


def _not_found_html(base):
    home = '{0}/'.format(base) if base else '/'
    return (
        '<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
        '<title>Страница не найдена</title></head><body>'
        '<p>Страница не найдена. <a href="{0}">Вернуться в кабинет</a>.</p>'
        '</body></html>\n'
    ).format(home)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Собрать статику DSA Lab')
    parser.add_argument(
        '--out',
        default=str(DEFAULT_OUT),
        help='Каталог сборки (по умолчанию ./site)',
    )
    parser.add_argument(
        '--base',
        default=os.environ.get('DSA_BASE_PATH', ''),
        help='Префикс URL, например /python-project-50',
    )
    args = parser.parse_args(argv)
    dest = export_site(args.out, args.base)
    lessons = ', '.join(item['slug'] for item in list_lessons())
    print('Static site → {0}'.format(dest))
    print('Base path: {0!r}'.format(normalize_base(args.base) or '/'))
    print('Lessons: {0}'.format(lessons))


if __name__ == '__main__':
    main()

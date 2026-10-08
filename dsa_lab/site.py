"""Общий контекст шаблонов для FastAPI и статического экспорта."""

from dsa_lab.content import list_lessons


def normalize_base(base):
    if not base or base == '/':
        return ''
    return '/' + str(base).strip('/')


def template_context(base='', dsa_static=False, **extra):
    context = {
        'base': normalize_base(base),
        'dsa_static': bool(dsa_static),
        'lessons': list_lessons(),
    }
    context.update(extra)
    return context

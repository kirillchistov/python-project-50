"""Общий контракт трассы и разбор пользовательского ввода."""


def make_trace(algorithm, complexity, steps):
    return {
        'meta': {
            'algorithm': algorithm,
            'complexity': complexity,
        },
        'steps': steps,
    }


def step(message, snapshot, highlight=None, focus=None):
    return {
        'message': message,
        'snapshot': snapshot,
        'highlight': highlight or {},
        'focus': focus or {},
    }


def parse_list(value, default=None):
    if value is None:
        return list(default or [])
    if isinstance(value, list):
        return [_coerce_item(item) for item in value]
    text = str(value).strip()
    if not text:
        return list(default or [])
    parts = [part.strip() for part in text.replace(';', ',').split(',')]
    return [_coerce_item(part) for part in parts if part]


def _coerce_item(item):
    if isinstance(item, bool):
        return item
    if isinstance(item, (int, float)):
        return item
    text = str(item).strip()
    if text.lower() in {'true', 'false'}:
        return text.lower() == 'true'
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def parse_int(value, default=0):
    if value is None or value == '':
        return default
    return int(value)


def array_snapshot(items, extra=None):
    snapshot = {
        'kind': 'array',
        'items': list(items),
    }
    if extra:
        snapshot.update(extra)
    return snapshot

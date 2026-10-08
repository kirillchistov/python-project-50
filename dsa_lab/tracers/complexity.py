from math import log2

from dsa_lab.tracers.base import make_trace, parse_int, step


def big_o(payload):
    size = max(2, min(parse_int(payload.get('n'), 24), 80))
    xs = list(range(1, size + 1))
    series = {
        'O(1)': [1 for _ in xs],
        'O(log n)': [max(1, int(log2(x))) for x in xs],
        'O(n)': xs[:],
        'O(n log n)': [int(x * max(1.0, log2(x))) for x in xs],
        'O(n²)': [x * x for x in xs],
    }
    quadratic = series['O(n²)'][-1]
    linear = series['O(n)'][-1]
    message = (
        'При n = {0} линейный проход — это {1} операций, а вложенный цикл '
        'уже {2}. Разница как между одной кассой и проверкой каждого '
        'покупателя каждой кассой.'
    ).format(size, linear, quadratic)
    return make_trace('big_o', 'зависит от класса', [step(
        message,
        {
            'kind': 'bigo',
            'n': size,
            'xs': xs,
            'series': series,
        },
    )])

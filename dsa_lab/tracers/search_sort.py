from dsa_lab.tracers.base import (
    array_snapshot,
    make_trace,
    parse_int,
    parse_list,
    step,
)


DEFAULT_ARRAY = [8, 3, 5, 1, 9, 2, 7, 4]


def linear_search(payload):
    items = parse_list(payload.get('array'), DEFAULT_ARRAY)
    target = payload.get('target', 5)
    target = _same_type(items, target)
    steps = []
    found = -1
    for index, value in enumerate(items):
        highlight = {'comparing': [index]}
        if value == target:
            found = index
            highlight['found'] = [index]
            steps.append(step(
                'Индекс {0}: {1} совпал с целью. Линейный поиск на этом '
                'останавливается.'.format(index, value),
                array_snapshot(items),
                highlight,
            ))
            break
        steps.append(step(
            'Индекс {0}: {1} ≠ {2}, идём дальше, как листая полку '
            'слева направо.'.format(index, value, target),
            array_snapshot(items),
            highlight,
        ))
    if found < 0:
        steps.append(step(
            'Значения {0} в массиве нет. Это худший случай: O(n).'.format(
                target,
            ),
            array_snapshot(items),
        ))
    return make_trace('linear_search', 'O(n) время, O(1) память', steps)


def binary_search(payload):
    raw = parse_list(payload.get('array'), DEFAULT_ARRAY)
    items = sorted(raw)
    target = _same_type(items, payload.get('target', 5))
    steps = [step(
        'Бинарный поиск работает только по отсортированным данным. '
        'Сначала сортируем: {0}.'.format(items),
        array_snapshot(items),
        {'sorted': list(range(len(items)))},
    )]
    lo = 0
    hi = len(items) - 1
    found = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        highlight = {
            'range': list(range(lo, hi + 1)),
            'pivot': [mid],
        }
        if items[mid] == target:
            found = mid
            highlight['found'] = [mid]
            steps.append(step(
                'Середина [{0}] = {1} — нашли, как открыв словарь '
                'сразу на нужной букве.'.format(mid, items[mid]),
                array_snapshot(items),
                highlight,
            ))
            break
        if items[mid] < target:
            steps.append(step(
                'Середина {0} < {1}, отбрасываем левую половину.'.format(
                    items[mid],
                    target,
                ),
                array_snapshot(items),
                highlight,
            ))
            lo = mid + 1
        else:
            steps.append(step(
                'Середина {0} > {1}, отбрасываем правую половину.'.format(
                    items[mid],
                    target,
                ),
                array_snapshot(items),
                highlight,
            ))
            hi = mid - 1
    if found < 0:
        steps.append(step(
            '{0} нет в массиве. Границы сомкнулись.'.format(target),
            array_snapshot(items),
        ))
    return make_trace('binary_search', 'O(log n) время, O(1) память', steps)


def bubble_sort(payload):
    items = parse_list(payload.get('array'), DEFAULT_ARRAY)
    steps = []
    n = len(items)
    for end in range(n - 1, 0, -1):
        swapped = False
        for index in range(end):
            highlight = {
                'comparing': [index, index + 1],
                'sorted': list(range(end + 1, n)),
            }
            left = items[index]
            right = items[index + 1]
            if left > right:
                items[index], items[index + 1] = right, left
                swapped = True
                highlight['swapping'] = [index, index + 1]
                steps.append(step(
                    '{0} > {1} — пузырёк всплывает, меняем местами.'.format(
                        left,
                        right,
                    ),
                    array_snapshot(items),
                    highlight,
                ))
            else:
                steps.append(step(
                    '{0} ≤ {1} — порядок верный, идём дальше.'.format(
                        left,
                        right,
                    ),
                    array_snapshot(items),
                    highlight,
                ))
        if not swapped:
            break
    steps.append(step(
        'Готово: каждый проход «всплывал» максимум в конец.',
        array_snapshot(items),
        {'sorted': list(range(len(items)))},
    ))
    return make_trace('bubble_sort', 'O(n²) время, O(1) память', steps)


def insertion_sort(payload):
    items = parse_list(payload.get('array'), DEFAULT_ARRAY)
    steps = [step(
        'Левая часть — уже разложенные карты в руке.',
        array_snapshot(items),
        {'sorted': [0]} if items else {},
    )]
    for index in range(1, len(items)):
        current = items[index]
        cursor = index
        steps.append(step(
            'Берём карту {0} и ищем ей место среди уже отсортированных.'.format(
                current,
            ),
            array_snapshot(items),
            {'pivot': [index], 'sorted': list(range(index))},
        ))
        while cursor > 0 and items[cursor - 1] > current:
            items[cursor] = items[cursor - 1]
            cursor -= 1
            items[cursor] = current
            steps.append(step(
                'Сдвигаем {0} вправо, чтобы освободить место.'.format(
                    items[cursor + 1],
                ),
                array_snapshot(items),
                {
                    'swapping': [cursor, cursor + 1],
                    'sorted': list(range(index + 1)),
                },
            ))
        items[cursor] = current
    steps.append(step(
        'Все карты в руке стоят по возрастанию.',
        array_snapshot(items),
        {'sorted': list(range(len(items)))},
    ))
    return make_trace('insertion_sort', 'O(n²) время, O(1) память', steps)


def merge_sort(payload):
    items = parse_list(payload.get('array'), DEFAULT_ARRAY)
    steps = []
    _merge_sort(items, 0, len(items), steps)
    steps.append(step(
        'Слияние собрало отсортированные половины — классика divide and conquer.',
        array_snapshot(items),
        {'sorted': list(range(len(items)))},
    ))
    return make_trace('merge_sort', 'O(n log n) время, O(n) память', steps)


def _merge_sort(items, lo, hi, steps):
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    steps.append(step(
        'Делим отрезок [{0}:{1}] пополам на [{0}:{2}] и [{2}:{1}].'.format(
            lo,
            hi,
            mid,
        ),
        array_snapshot(items, {'ranges': [{'lo': lo, 'hi': hi - 1}]}),
        {'range': list(range(lo, hi))},
    ))
    _merge_sort(items, lo, mid, steps)
    _merge_sort(items, mid, hi, steps)
    merged = _merge(items[lo:mid], items[mid:hi])
    items[lo:hi] = merged
    steps.append(step(
        'Сливаем половины в [{0}:{1}] → {2}.'.format(lo, hi, merged),
        array_snapshot(items, {'ranges': [{'lo': lo, 'hi': hi - 1}]}),
        {'sorted': list(range(lo, hi))},
    ))


def _merge(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(payload):
    items = parse_list(payload.get('array'), DEFAULT_ARRAY)
    steps = []
    _quick_sort(items, 0, len(items) - 1, steps)
    steps.append(step(
        'Опорные элементы разъехались по своим местам. Массив отсортирован.',
        array_snapshot(items),
        {'sorted': list(range(len(items)))},
    ))
    return make_trace('quick_sort', 'в среднем O(n log n), память O(log n)', steps)


def _quick_sort(items, lo, hi, steps):
    if lo >= hi:
        return
    pivot = items[hi]
    steps.append(step(
        'Опора — последний элемент {0}. Меньшие влево, большие вправо.'.format(
            pivot,
        ),
        array_snapshot(items),
        {'pivot': [hi], 'range': list(range(lo, hi + 1))},
    ))
    boundary = lo
    for index in range(lo, hi):
        highlight = {
            'pivot': [hi],
            'comparing': [index],
            'range': list(range(lo, hi)),
        }
        if items[index] <= pivot:
            items[boundary], items[index] = items[index], items[boundary]
            highlight['swapping'] = [boundary, index]
            steps.append(step(
                '{0} ≤ опоры, ставим в левую зону на позицию {1}.'.format(
                    items[boundary],
                    boundary,
                ),
                array_snapshot(items),
                highlight,
            ))
            boundary += 1
        else:
            steps.append(step(
                '{0} больше опоры, пока оставляем справа.'.format(items[index]),
                array_snapshot(items),
                highlight,
            ))
    items[boundary], items[hi] = items[hi], items[boundary]
    steps.append(step(
        'Опора встала на индекс {0}. Её место уже финальное.'.format(boundary),
        array_snapshot(items),
        {'found': [boundary]},
    ))
    _quick_sort(items, lo, boundary - 1, steps)
    _quick_sort(items, boundary + 1, hi, steps)


def _same_type(items, target):
    if isinstance(target, str) and target.strip().lstrip('-').isdigit():
        target = parse_int(target, 0)
    if items and isinstance(items[0], int) and not isinstance(target, int):
        try:
            return int(target)
        except (TypeError, ValueError):
            return target
    return target

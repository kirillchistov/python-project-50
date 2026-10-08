from dsa_lab.tracers.base import make_trace, parse_list, step


def stack(payload):
    operations = _operations(payload, ['push:заказ A', 'push:заказ B', 'push:заказ C', 'pop', 'push:заказ D'])
    items = []
    steps = [step(
        'Стек — стопка тарелок: кладём и снимаем только сверху (LIFO).',
        {'kind': 'stack', 'items': []},
    )]
    for operation in operations:
        name, value = _split_op(operation)
        if name == 'push':
            items.append(value)
            steps.append(step(
                'push({0}): новая тарелка сверху.'.format(value),
                {'kind': 'stack', 'items': list(items)},
                {'head': [len(items) - 1]},
            ))
        elif name == 'pop':
            if not items:
                steps.append(step(
                    'pop() на пустом стеке — ошибка. Так падает call stack overflow наоборот.',
                    {'kind': 'stack', 'items': []},
                ))
                continue
            taken = items.pop()
            steps.append(step(
                'pop() → {0}. Сняли верхнюю тарелку.'.format(taken),
                {'kind': 'stack', 'items': list(items)},
                {'head': [len(items) - 1]} if items else {},
            ))
    return make_trace('stack', 'O(1) push/pop', steps)


def queue_trace(payload):
    operations = _operations(
        payload,
        ['enqueue:Аня', 'enqueue:Борис', 'enqueue:Кира', 'dequeue', 'enqueue:Дима'],
    )
    items = []
    steps = [step(
        'Очередь в кассу: первый пришёл — первый ушёл (FIFO).',
        {'kind': 'queue', 'items': []},
    )]
    for operation in operations:
        name, value = _split_op(operation)
        if name in {'enqueue', 'push'}:
            items.append(value)
            steps.append(step(
                'enqueue({0}): встал в хвост.'.format(value),
                {'kind': 'queue', 'items': list(items)},
                {'tail': [len(items) - 1]},
            ))
        elif name in {'dequeue', 'pop'}:
            if not items:
                steps.append(step(
                    'dequeue() из пустой очереди нечего взять.',
                    {'kind': 'queue', 'items': []},
                ))
                continue
            taken = items.pop(0)
            steps.append(step(
                'dequeue() → {0}: обслужили голову очереди.'.format(taken),
                {'kind': 'queue', 'items': list(items)},
                {'head': [0]} if items else {},
            ))
    return make_trace('queue', 'O(1) enqueue, dequeue на deque', steps)


def linked_list(payload):
    values = parse_list(payload.get('array'), ['хост', 'таймаут', 'прокси'])
    nodes = []
    steps = [step(
        'Односвязный список — вагоны: у каждого есть ссылка только вперёд.',
        {'kind': 'list', 'nodes': []},
    )]
    for index, value in enumerate(values):
        node = {'id': index, 'value': value, 'next': None}
        if nodes:
            nodes[-1]['next'] = index
        nodes.append(node)
        steps.append(step(
            'Прицепили вагон «{0}». Вставка в хвост без массива копирования.'.format(
                value,
            ),
            _list_snapshot(nodes),
            {'head': [0], 'tail': [index]},
        ))
    if len(nodes) >= 2:
        steps.append(step(
            'Чтобы достать третий элемент, идём по цепочке: O(n), в отличие от массива.',
            _list_snapshot(nodes),
            {'comparing': [0, 1, min(2, len(nodes) - 1)]},
        ))
    return make_trace('linked_list', 'O(1) вставка с известным узлом, O(n) доступ', steps)


def hash_table(payload):
    keys = parse_list(
        payload.get('array'),
        ['host', 'timeout', 'proxy', 'verbose', 'follow'],
    )
    bucket_count = 4
    buckets = [[] for _ in range(bucket_count)]
    steps = [step(
        'Хеш-таблица — шкафчики: номер = hash(ключ) mod {0}.'.format(
            bucket_count,
        ),
        {'kind': 'hash', 'buckets': [[] for _ in range(bucket_count)]},
    )]
    for key in keys:
        index = _hash_key(key, bucket_count)
        collided = bool(buckets[index])
        buckets[index].append(key)
        message = 'Ключ «{0}» попал в ячейку {1}.'.format(key, index)
        if collided:
            message += ' Коллизия: в шкафчике уже кто-то есть, вешаем цепочку.'
        steps.append(step(
            message,
            {
                'kind': 'hash',
                'buckets': [list(bucket) for bucket in buckets],
            },
            {'bucket': [index]},
        ))
    steps.append(step(
        'Поиск host: считаем хеш и смотрим одну ячейку — в среднем O(1). '
        'Именно так Python dict хранит JSON-ключи в gendiff.',
        {
            'kind': 'hash',
            'buckets': [list(bucket) for bucket in buckets],
        },
        {'found-key': ['host']},
    ))
    return make_trace('hash_table', 'в среднем O(1) поиск/вставка', steps)


def _list_snapshot(nodes):
    return {
        'kind': 'list',
        'nodes': [
            {
                'id': node['id'],
                'value': node['value'],
                'next': node['next'],
            }
            for node in nodes
        ],
    }


def _operations(payload, default):
    raw = payload.get('operations', default)
    if isinstance(raw, str):
        return [part.strip() for part in raw.split('\n') if part.strip()]
    return list(raw)


def _split_op(operation):
    if ':' in str(operation):
        name, value = str(operation).split(':', 1)
        return name.strip().lower(), value.strip()
    return str(operation).strip().lower(), ''


def _hash_key(key, bucket_count):
    return sum(ord(char) for char in str(key)) % bucket_count

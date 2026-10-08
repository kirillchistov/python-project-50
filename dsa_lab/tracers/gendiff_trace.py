import json
from copy import deepcopy

from dsa_lab.tracers.base import make_trace, step


DEFAULT_LEFT = {
    'host': 'hexlet.io',
    'timeout': 50,
    'proxy': '123.234.53.22',
    'common': {
        'setting': 'on',
        'doge': {'wow': ''},
    },
}

DEFAULT_RIGHT = {
    'host': 'hexlet.io',
    'timeout': 20,
    'verbose': True,
    'common': {
        'setting': 'on',
        'doge': {'wow': 'so much'},
    },
}


def gendiff_build(payload):
    left = _as_mapping(payload.get('left'), DEFAULT_LEFT)
    right = _as_mapping(payload.get('right'), DEFAULT_RIGHT)
    collector = []
    stack = []
    result = _walk(left, right, '', stack, collector, left, right)
    collector.append(step(
        'Дерево diff собрано. Дальше форматтер обойдёт его в глубину — как stylish.walk.',
        _snapshot(left, right, '', stack, result),
        {'done': True},
    ))
    return make_trace(
        'gendiff_build',
        'O(k log k) на уровень, память — дерево узлов',
        collector,
    )


def stylish_walk(payload):
    left = _as_mapping(payload.get('left'), DEFAULT_LEFT)
    right = _as_mapping(payload.get('right'), DEFAULT_RIGHT)
    diff = _silent_build(left, right)
    collector = []
    stack = []
    _walk_format(diff, 1, stack, collector, diff)
    collector.append(step(
        'Обход закончен: это DFS pre-order, тот же порядок, что у format_stylish.',
        {
            'kind': 'gendiff',
            'tree': diff,
            'stack': [],
            'path': '',
            'left': left,
            'right': right,
            'lines': _collect_keys(diff),
        },
    ))
    return make_trace('stylish_walk', 'O(n) по числу узлов дерева', collector)


def _walk(data1, data2, path, stack, collector, root_left, root_right):
    frame = path or 'корень'
    stack.append('build_diff({0})'.format(frame))
    keys = sorted(data1.keys() | data2.keys())
    collector.append(step(
        'Уровень «{0}»: объединили ключи как множества и отсортировали → {1}.'.format(
            frame,
            keys,
        ),
        _snapshot(root_left, root_right, path, stack, []),
        {'keys': keys},
    ))
    diff = []
    for key in keys:
        child_path = '{0}.{1}'.format(path, key) if path else key
        node = _classify(key, data1, data2, child_path, stack, collector, root_left, root_right)
        diff.append(node)
        collector.append(step(
            _node_message(node, child_path),
            _snapshot(root_left, root_right, child_path, stack, diff),
            {'node_type': node['type'], 'key': key},
        ))
    stack.pop()
    return diff


def _classify(key, data1, data2, path, stack, collector, root_left, root_right):
    value1 = data1.get(key)
    value2 = data2.get(key)
    if key not in data1:
        return {'key': key, 'type': 'added', 'value': value2}
    if key not in data2:
        return {'key': key, 'type': 'removed', 'value': value1}
    if _is_dict(value1) and _is_dict(value2):
        collector.append(step(
            'И «{0}», и справа — словари. Ныряем глубже, как в матрёшку.'.format(
                path,
            ),
            _snapshot(root_left, root_right, path, stack, []),
            {'node_type': 'nested', 'key': key},
        ))
        children = _walk(
            value1,
            value2,
            path,
            stack,
            collector,
            root_left,
            root_right,
        )
        return {'key': key, 'type': 'nested', 'children': children}
    if value1 == value2:
        return {'key': key, 'type': 'unchanged', 'value': value1}
    return {
        'key': key,
        'type': 'changed',
        'old_value': value1,
        'new_value': value2,
    }


def _silent_build(data1, data2):
    keys = sorted(data1.keys() | data2.keys())
    diff = []
    for key in keys:
        value1 = data1.get(key)
        value2 = data2.get(key)
        if key not in data1:
            diff.append({'key': key, 'type': 'added', 'value': value2})
        elif key not in data2:
            diff.append({'key': key, 'type': 'removed', 'value': value1})
        elif _is_dict(value1) and _is_dict(value2):
            diff.append({
                'key': key,
                'type': 'nested',
                'children': _silent_build(value1, value2),
            })
        elif value1 == value2:
            diff.append({'key': key, 'type': 'unchanged', 'value': value1})
        else:
            diff.append({
                'key': key,
                'type': 'changed',
                'old_value': value1,
                'new_value': value2,
            })
    return diff


def _walk_format(nodes, depth, stack, collector, tree):
    for node in nodes:
        key = node['key']
        stack.append('walk({0})'.format(key))
        collector.append(step(
            'DFS: зашли в узел «{0}» (тип {1}), глубина {2}.'.format(
                key,
                node['type'],
                depth,
            ),
            {
                'kind': 'gendiff',
                'tree': tree,
                'stack': list(stack),
                'path': key,
                'left': {},
                'right': {},
                'focus_key': key,
            },
            {'node_type': node['type'], 'key': key},
        ))
        if node['type'] == 'nested':
            _walk_format(node['children'], depth + 1, stack, collector, tree)
        stack.pop()


def _snapshot(left, right, path, stack, tree):
    return {
        'kind': 'gendiff',
        'left': left,
        'right': right,
        'path': path,
        'stack': list(stack),
        'tree': deepcopy(tree),
    }


def _node_message(node, path):
    labels = {
        'added': 'появился только справа (+)',
        'removed': 'пропал справа (−)',
        'changed': 'значение изменилось',
        'unchanged': 'совпадает — оставляем как якорь',
        'nested': 'вложенный узел, дети уже собраны',
    }
    return 'Ключ «{0}»: {1}.'.format(path, labels[node['type']])


def _collect_keys(nodes):
    keys = []
    for node in nodes:
        keys.append(node['key'])
        if node.get('type') == 'nested':
            keys.extend(_collect_keys(node['children']))
    return keys


def _is_dict(value):
    return isinstance(value, dict)


def _as_mapping(value, default):
    if value is None or value == '':
        return deepcopy(default)
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        loaded = json.loads(value)
        if not isinstance(loaded, dict):
            raise ValueError('Ожидался JSON-объект')
        return loaded
    raise ValueError('left/right должны быть объектами')

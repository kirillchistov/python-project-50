from dsa_lab.tracers.base import make_trace, parse_int, parse_list, step


class Node:
    def __init__(self, key, ident):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1
        self.ident = ident


def bst(payload):
    values = parse_list(payload.get('array'), [8, 3, 10, 1, 6, 14])
    target = payload.get('target', 6)
    if isinstance(target, str) and target.strip():
        target = parse_int(target, 6)
    steps = []
    ident = [0]
    holder = {'root': None}
    for value in values:
        holder['root'] = _bst_insert(holder['root'], value, ident, steps, holder)
    steps.append(step(
        'Дерево поиска построено: влево — меньше, вправо — больше, как оргсхема.',
        _tree_snapshot(holder['root']),
    ))
    _bst_search(holder['root'], target, steps)
    return make_trace('bst', 'в среднем O(log n), худший O(n)', steps)


def avl_insert(payload):
    values = parse_list(payload.get('array'), [10, 20, 30, 40, 50, 25])
    steps = []
    ident = [0]
    holder = {'root': None}
    for value in values:
        holder['root'] = _avl_insert(holder['root'], value, ident, steps, holder)
        steps.append(step(
            'После вставки {0} дерево снова сбалансировано (разница высот ≤ 1).'.format(
                value,
            ),
            _tree_snapshot(holder['root']),
            {'focus': [value]},
        ))
    return make_trace('avl_insert', 'O(log n) вставка за счёт поворотов', steps)


def _bst_insert(node, key, ident, steps, holder):
    if node is None:
        ident[0] += 1
        created = Node(key, ident[0])
        steps.append(step(
            'Создаём лист {0}.'.format(key),
            _tree_snapshot(holder['root'] or created),
            {'focus': [key]},
        ))
        return created
    steps.append(step(
        'Сравниваем {0} с узлом {1}.'.format(key, node.key),
        _tree_snapshot(holder['root']),
        {'comparing': [node.key], 'focus': [key]},
    ))
    if key < node.key:
        node.left = _bst_insert(node.left, key, ident, steps, holder)
    elif key > node.key:
        node.right = _bst_insert(node.right, key, ident, steps, holder)
    return node


def _bst_search(node, target, steps):
    current = node
    while current is not None:
        if current.key == target:
            steps.append(step(
                'Нашли {0}. В сбалансированном дереве это как спуск по оргсхеме.'.format(
                    target,
                ),
                _tree_snapshot(node),
                {'found': [target]},
            ))
            return
        go_left = target < current.key
        steps.append(step(
            '{0} {1} {2} — идём {3}.'.format(
                target,
                '<' if go_left else '>',
                current.key,
                'влево' if go_left else 'вправо',
            ),
            _tree_snapshot(node),
            {'comparing': [current.key]},
        ))
        current = current.left if go_left else current.right
    steps.append(step(
        '{0} в дереве нет.'.format(target),
        _tree_snapshot(node),
    ))


def _avl_insert(node, key, ident, steps, holder):
    if node is None:
        ident[0] += 1
        return Node(key, ident[0])
    if key < node.key:
        node.left = _avl_insert(node.left, key, ident, steps, holder)
    elif key > node.key:
        node.right = _avl_insert(node.right, key, ident, steps, holder)
    else:
        return node
    _update_height(node)
    balance = _balance(node)
    if balance > 1 and key < node.left.key:
        steps.append(step(
            'Левый-левый случай у {0}: малый правый поворот.'.format(node.key),
            _tree_snapshot(holder['root']),
            {'pivot': [node.key]},
        ))
        return _rotate_right(node)
    if balance < -1 and key > node.right.key:
        steps.append(step(
            'Правый-правый случай у {0}: малый левый поворот.'.format(node.key),
            _tree_snapshot(holder['root']),
            {'pivot': [node.key]},
        ))
        return _rotate_left(node)
    if balance > 1 and key > node.left.key:
        steps.append(step(
            'Левый-правый у {0}: сначала левый поворот, затем правый.'.format(
                node.key,
            ),
            _tree_snapshot(holder['root']),
            {'pivot': [node.key]},
        ))
        node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if balance < -1 and key < node.right.key:
        steps.append(step(
            'Правый-левый у {0}: сначала правый поворот, затем левый.'.format(
                node.key,
            ),
            _tree_snapshot(holder['root']),
            {'pivot': [node.key]},
        ))
        node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


def _height(node):
    return node.height if node else 0


def _balance(node):
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)


def _update_height(node):
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_left(z_node):
    y_node = z_node.right
    subtree = y_node.left
    y_node.left = z_node
    z_node.right = subtree
    _update_height(z_node)
    _update_height(y_node)
    return y_node


def _rotate_right(z_node):
    y_node = z_node.left
    subtree = y_node.right
    y_node.right = z_node
    z_node.left = subtree
    _update_height(z_node)
    _update_height(y_node)
    return y_node


def _tree_snapshot(root):
    nodes = []

    def walk(node):
        if node is None:
            return None
        nodes.append({
            'id': node.ident,
            'value': node.key,
            'left': node.left.ident if node.left else None,
            'right': node.right.ident if node.right else None,
            'balance': _balance(node),
            'height': node.height,
        })
        walk(node.left)
        walk(node.right)
        return node.ident

    root_id = walk(root)
    return {
        'kind': 'tree',
        'root': root_id,
        'nodes': nodes,
    }

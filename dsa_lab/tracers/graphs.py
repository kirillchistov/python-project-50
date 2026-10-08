from dsa_lab.tracers.base import make_trace, step


DEFAULT_NODES = [
    {'id': 'A', 'label': 'Сокол', 'x': 40, 'y': 40},
    {'id': 'B', 'label': 'Аэропорт', 'x': 200, 'y': 40},
    {'id': 'C', 'label': 'Динамо', 'x': 360, 'y': 40},
    {'id': 'D', 'label': 'Белорусская', 'x': 40, 'y': 180},
    {'id': 'E', 'label': 'Маяковская', 'x': 200, 'y': 180},
    {'id': 'F', 'label': 'Тверская', 'x': 360, 'y': 180},
]

DEFAULT_EDGES = [
    {'source': 'A', 'target': 'B', 'weight': 2},
    {'source': 'B', 'target': 'C', 'weight': 3},
    {'source': 'A', 'target': 'D', 'weight': 1},
    {'source': 'B', 'target': 'E', 'weight': 4},
    {'source': 'C', 'target': 'F', 'weight': 2},
    {'source': 'D', 'target': 'E', 'weight': 2},
    {'source': 'E', 'target': 'F', 'weight': 1},
]


def bfs(payload):
    start = payload.get('start', 'A')
    graph = _adj()
    queue = [start]
    visited = {start}
    order = []
    steps = [step(
        'BFS — обход волнами, как метро: сначала все соседние станции.',
        _graph_snapshot([], [], start),
        {'frontier': [start]},
    )]
    while queue:
        current = queue.pop(0)
        order.append(current)
        steps.append(step(
            'Выходим на станции {0}. Очередь: {1}.'.format(
                _label(current),
                [_label(item) for item in queue],
            ),
            _graph_snapshot(order, queue, current),
            {'current': [current], 'visited': order[:], 'frontier': queue[:]},
        ))
        for neighbor, _weight in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                steps.append(step(
                    'Видим соседа {0}, кладём в очередь.'.format(_label(neighbor)),
                    _graph_snapshot(order, queue, current),
                    {
                        'current': [current],
                        'visited': list(visited),
                        'frontier': queue[:],
                    },
                ))
    steps.append(step(
        'Порядок обхода: {0}.'.format(' → '.join(_label(item) for item in order)),
        _graph_snapshot(order, [], None),
        {'visited': order},
    ))
    return make_trace('bfs', 'O(V + E) время', steps)


def dfs(payload):
    start = payload.get('start', 'A')
    graph = _adj()
    order = []
    steps = []
    visited = set()

    def visit(node):
        visited.add(node)
        order.append(node)
        steps.append(step(
            'DFS: ныряем в {0}, как в глухой переулок, пока есть куда идти.'.format(
                _label(node),
            ),
            _graph_snapshot(order, [], node),
            {'current': [node], 'visited': order[:]},
        ))
        for neighbor, _weight in graph[node]:
            if neighbor not in visited:
                visit(neighbor)

    visit(start)
    steps.append(step(
        'Порядок DFS: {0}. Тот же принцип, что walk() в stylish.'.format(
            ' → '.join(_label(item) for item in order),
        ),
        _graph_snapshot(order, [], None),
        {'visited': order},
    ))
    return make_trace('dfs', 'O(V + E) время', steps)


def dijkstra(payload):
    start = payload.get('start', 'A')
    graph = _adj()
    nodes = [node['id'] for node in DEFAULT_NODES]
    dist = {node: float('inf') for node in nodes}
    dist[start] = 0
    prev = {node: None for node in nodes}
    used = set()
    steps = [step(
        'Дейкстра: от {0} ищем кратчайшие пути, как навигатору в городе.'.format(
            _label(start),
        ),
        _graph_snapshot([], [], start, dist),
        {'current': [start]},
    )]
    for _ in nodes:
        current = _min_unused(dist, used)
        if current is None or dist[current] == float('inf'):
            break
        used.add(current)
        steps.append(step(
            'Фиксируем {0} с расстоянием {1}.'.format(
                _label(current),
                dist[current],
            ),
            _graph_snapshot(list(used), [], current, dist),
            {'current': [current], 'visited': list(used)},
        ))
        for neighbor, weight in graph[current]:
            candidate = dist[current] + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                prev[neighbor] = current
                steps.append(step(
                    'Через {0} до {1} дешевле: {2}.'.format(
                        _label(current),
                        _label(neighbor),
                        candidate,
                    ),
                    _graph_snapshot(list(used), [], current, dist),
                    {
                        'current': [current],
                        'focus': [neighbor],
                        'visited': list(used),
                    },
                ))
    steps.append(step(
        'Кратчайшие расстояния: {0}.'.format(
            ', '.join(
                '{0}={1}'.format(_label(node), dist[node])
                for node in nodes
            ),
        ),
        _graph_snapshot(list(used), [], start, dist, prev),
        {'visited': list(used)},
    ))
    return make_trace('dijkstra', 'O((V + E) log V) с кучей', steps)


def floyd(payload):
    nodes = [node['id'] for node in DEFAULT_NODES]
    dist = {src: {dst: float('inf') for dst in nodes} for src in nodes}
    for node in nodes:
        dist[node][node] = 0
    for edge in DEFAULT_EDGES:
        dist[edge['source']][edge['target']] = edge['weight']
        dist[edge['target']][edge['source']] = edge['weight']
    steps = [step(
        'Флойд — Уоршелл: кратчайшие пути между всеми парами станций.',
        {'kind': 'table', 'matrix': _matrix(dist, nodes), 'labels': [_label(n) for n in nodes]},
    )]
    for mid in nodes:
        for src in nodes:
            for dst in nodes:
                via = dist[src][mid] + dist[mid][dst]
                if via < dist[src][dst]:
                    dist[src][dst] = via
                    steps.append(step(
                        'Через {0} путь {1} → {2} стал {3}.'.format(
                            _label(mid),
                            _label(src),
                            _label(dst),
                            via,
                        ),
                        {
                            'kind': 'table',
                            'matrix': _matrix(dist, nodes),
                            'labels': [_label(node) for node in nodes],
                        },
                        {
                            'cell': [nodes.index(src), nodes.index(dst)],
                            'via': mid,
                        },
                    ))
    steps.append(step(
        'Матрица заполнена. Память O(V²) — цена «знать всё обо всех».',
        {
            'kind': 'table',
            'matrix': _matrix(dist, nodes),
            'labels': [_label(node) for node in nodes],
        },
    ))
    return make_trace('floyd', 'O(V³) время, O(V²) память', steps)


def _adj():
    graph = {node['id']: [] for node in DEFAULT_NODES}
    for edge in DEFAULT_EDGES:
        graph[edge['source']].append((edge['target'], edge['weight']))
        graph[edge['target']].append((edge['source'], edge['weight']))
    return graph


def _label(node_id):
    for node in DEFAULT_NODES:
        if node['id'] == node_id:
            return node['label']
    return node_id


def _graph_snapshot(visited, frontier, current, dist=None, prev=None):
    return {
        'kind': 'graph',
        'nodes': DEFAULT_NODES,
        'edges': DEFAULT_EDGES,
        'visited': visited,
        'frontier': frontier,
        'current': current,
        'dist': _plain_dist(dist) if dist else {},
        'prev': prev or {},
    }


def _plain_dist(dist):
    result = {}
    for key, value in dist.items():
        result[key] = None if value == float('inf') else value
    return result


def _min_unused(dist, used):
    best = None
    best_value = float('inf')
    for node, value in dist.items():
        if node in used:
            continue
        if value < best_value:
            best = node
            best_value = value
    return best


def _matrix(dist, nodes):
    rows = []
    for src in nodes:
        row = []
        for dst in nodes:
            value = dist[src][dst]
            row.append(None if value == float('inf') else value)
        rows.append(row)
    return rows

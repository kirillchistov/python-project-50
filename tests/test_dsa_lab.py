import json
from pathlib import Path

from gendiff.builder import build_diff
from gendiff.parser import parse_file

from dsa_lab.content import get_lesson, list_lessons
from dsa_lab.tracers import ALGORITHMS, run_trace
from dsa_lab.tracers.gendiff_trace import DEFAULT_LEFT, DEFAULT_RIGHT


def _last_array(trace):
    return trace['steps'][-1]['snapshot']['items']


def test_all_algorithms_registered():
    expected = {
        'big_o',
        'linear_search',
        'binary_search',
        'bubble_sort',
        'insertion_sort',
        'merge_sort',
        'quick_sort',
        'stack',
        'queue',
        'hash_table',
        'linked_list',
        'bst',
        'avl_insert',
        'bfs',
        'dfs',
        'dijkstra',
        'floyd',
        'coin_change_greedy',
        'coin_change_dp',
        'gendiff_build',
        'stylish_walk',
    }
    assert set(ALGORITHMS) == expected


def test_linear_search_finds_index():
    trace = run_trace('linear_search', {'array': [8, 3, 5, 1], 'target': 5})
    found = trace['steps'][-1]['highlight']['found']
    assert found == [2]


def test_binary_search_finds_index():
    trace = run_trace('binary_search', {'array': [8, 3, 5, 1, 9], 'target': 5})
    assert trace['steps'][-1]['highlight']['found'] == [2]


def test_sorts_end_sorted():
    source = [8, 3, 5, 1, 9, 2, 7, 4]
    for name in ('bubble_sort', 'insertion_sort', 'merge_sort', 'quick_sort'):
        trace = run_trace(name, {'array': source[:]})
        assert _last_array(trace) == sorted(source)


def test_gendiff_trace_matches_builder():
    trace = run_trace(
        'gendiff_build',
        {'left': DEFAULT_LEFT, 'right': DEFAULT_RIGHT},
    )
    actual = trace['steps'][-1]['snapshot']['tree']
    assert actual == build_diff(DEFAULT_LEFT, DEFAULT_RIGHT)


def test_gendiff_trace_on_project_fixtures():
    root = Path(__file__).resolve().parents[1]
    left = parse_file(root / 'gendiff' / 'files' / 'nested1.json')
    right = parse_file(root / 'gendiff' / 'files' / 'nested2.json')
    trace = run_trace('gendiff_build', {'left': left, 'right': right})
    assert trace['steps'][-1]['snapshot']['tree'] == build_diff(left, right)


def test_coin_change_greedy_loses_to_dp():
    payload = {'array': [1, 3, 4], 'amount': 6}
    greedy = run_trace('coin_change_greedy', payload)
    dp_trace = run_trace('coin_change_dp', payload)
    greedy_coins = [item for item in greedy['steps'][-1]['snapshot']['items'] if item != '—']
    dp_table = dp_trace['steps'][-1]['snapshot']['matrix'][0]
    assert len(greedy_coins) == 3
    assert dp_table[6] == 2


def test_bfs_visits_all_stations():
    trace = run_trace('bfs', {'start': 'A'})
    visited = trace['steps'][-1]['highlight']['visited']
    assert set(visited) == {'A', 'B', 'C', 'D', 'E', 'F'}


def test_bst_finds_target():
    trace = run_trace('bst', {'array': [8, 3, 10, 1, 6, 14], 'target': 6})
    assert 'found' in trace['steps'][-1]['highlight']


def test_lessons_catalog():
    lessons = list_lessons()
    assert len(lessons) == 7
    assert get_lesson('recursion')['slug'] == 'recursion'
    assert get_lesson('missing') is None


def test_trace_payload_accepts_json_strings():
    trace = run_trace(
        'gendiff_build',
        {
            'left': json.dumps({'a': 1}),
            'right': json.dumps({'a': 2, 'b': 3}),
        },
    )
    types = {node['key']: node['type'] for node in trace['steps'][-1]['snapshot']['tree']}
    assert types == {'a': 'changed', 'b': 'added'}


def test_export_static_site(tmp_path):
    from dsa_lab.export_static import export_site
    from dsa_lab.site import normalize_base

    assert normalize_base('/python-project-50/') == '/python-project-50'
    assert normalize_base('/') == ''

    dest = export_site(tmp_path / 'site', base='/python-project-50')
    index = (dest / 'index.html').read_text(encoding='utf-8')
    assert 'DSA_STATIC = true' in index
    assert '/python-project-50/static/css/app.css' in index
    assert '/python-project-50/lessons/recursion' in index
    assert (dest / 'lessons' / 'recursion' / 'index.html').exists()
    assert (dest / 'static' / 'js' / 'tracers.js').exists()
    assert (dest / '.nojekyll').exists()
    assert (dest / '404.html').exists()

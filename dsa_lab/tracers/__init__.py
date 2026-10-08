from dsa_lab.tracers.complexity import big_o
from dsa_lab.tracers.dp import coin_change_dp, coin_change_greedy
from dsa_lab.tracers.gendiff_trace import gendiff_build, stylish_walk
from dsa_lab.tracers.graphs import bfs, dfs, dijkstra, floyd
from dsa_lab.tracers.search_sort import (
    binary_search,
    bubble_sort,
    insertion_sort,
    linear_search,
    merge_sort,
    quick_sort,
)
from dsa_lab.tracers.structures import (
    hash_table,
    linked_list,
    queue_trace,
    stack,
)
from dsa_lab.tracers.trees import avl_insert, bst


ALGORITHMS = {
    'big_o': big_o,
    'linear_search': linear_search,
    'binary_search': binary_search,
    'bubble_sort': bubble_sort,
    'insertion_sort': insertion_sort,
    'merge_sort': merge_sort,
    'quick_sort': quick_sort,
    'stack': stack,
    'queue': queue_trace,
    'hash_table': hash_table,
    'linked_list': linked_list,
    'bst': bst,
    'avl_insert': avl_insert,
    'bfs': bfs,
    'dfs': dfs,
    'dijkstra': dijkstra,
    'floyd': floyd,
    'coin_change_greedy': coin_change_greedy,
    'coin_change_dp': coin_change_dp,
    'gendiff_build': gendiff_build,
    'stylish_walk': stylish_walk,
}


def run_trace(algorithm, payload):
    if algorithm not in ALGORITHMS:
        raise KeyError(algorithm)
    return ALGORITHMS[algorithm](payload or {})

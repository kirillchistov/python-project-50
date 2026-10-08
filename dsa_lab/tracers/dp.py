from dsa_lab.tracers.base import make_trace, parse_int, parse_list, step


DEFAULT_COINS = [1, 3, 4]


def coin_change_greedy(payload):
    coins = sorted(parse_list(payload.get('array'), DEFAULT_COINS), reverse=True)
    amount = parse_int(payload.get('amount'), 6)
    left = amount
    taken = []
    steps = [step(
        'Жадный алгоритм берёт самую крупную монету, которая ещё влезает. '
        'Как набирать сдачу «на глаз».',
        _coins_snapshot(coins, taken, left),
    )]
    for coin in coins:
        while left >= coin:
            taken.append(coin)
            left -= coin
            steps.append(step(
                'Берём {0}, осталось {1}.'.format(coin, left),
                _coins_snapshot(coins, taken, left),
                {'focus': [coin]},
            ))
    if left:
        steps.append(step(
            'Не удалось набрать сумму. Жадность не всегда справляется.',
            _coins_snapshot(coins, taken, left),
        ))
    else:
        steps.append(step(
            'Набрали {0} монетами: {1}. Для {2} и суммы 6 это 4+1+1 — не оптимум.'.format(
                len(taken),
                taken,
                coins,
            ),
            _coins_snapshot(coins, taken, 0),
        ))
    return make_trace('coin_change_greedy', 'O(k) по номиналам', steps)


def coin_change_dp(payload):
    coins = sorted(parse_list(payload.get('array'), DEFAULT_COINS))
    amount = parse_int(payload.get('amount'), 6)
    inf = amount + 1
    table = [inf] * (amount + 1)
    table[0] = 0
    choice = [None] * (amount + 1)
    steps = [step(
        'DP: dp[x] — минимум монет для суммы x. Не пересчитываем одно и то же.',
        {
            'kind': 'table',
            'matrix': [table[:]],
            'labels': [str(index) for index in range(amount + 1)],
            'row_labels': ['dp'],
        },
    )]
    for current in range(1, amount + 1):
        for coin in coins:
            if coin > current:
                continue
            candidate = table[current - coin] + 1
            if candidate < table[current]:
                table[current] = candidate
                choice[current] = coin
                steps.append(step(
                    'Для суммы {0} вариант с монетой {1} даёт {2} шт.'.format(
                        current,
                        coin,
                        candidate,
                    ),
                    {
                        'kind': 'table',
                        'matrix': [table[:]],
                        'labels': [str(index) for index in range(amount + 1)],
                        'row_labels': ['dp'],
                    },
                    {'cell': [0, current]},
                ))
    coins_used = _restore(choice, amount)
    steps.append(step(
        'Оптимум для {0}: {1} монет {2}. Для [1, 3, 4] и 6 это 3+3, лучше жадного.'.format(
            amount,
            table[amount],
            coins_used,
        ),
        {
            'kind': 'table',
            'matrix': [table[:]],
            'labels': [str(index) for index in range(amount + 1)],
            'row_labels': ['dp'],
        },
        {'cell': [0, amount]},
    ))
    return make_trace('coin_change_dp', 'O(amount × k) время, O(amount) память', steps)


def _restore(choice, amount):
    coins = []
    current = amount
    while current > 0 and choice[current] is not None:
        coins.append(choice[current])
        current -= choice[current]
    return coins


def _coins_snapshot(coins, taken, left):
    return {
        'kind': 'array',
        'items': taken or ['—'],
        'caption': 'номиналы {0}, остаток {1}'.format(coins, left),
    }

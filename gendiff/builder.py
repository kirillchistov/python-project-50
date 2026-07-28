def is_dict(value):
    return isinstance(value, dict)


def build_diff(data1, data2):
    keys = sorted(data1.keys() | data2.keys())
    diff = []

    for key in keys:
        value1 = data1.get(key)
        value2 = data2.get(key)

        if key not in data1:
            diff.append({
                'key': key,
                'type': 'added',
                'value': value2,
            })
        elif key not in data2:
            diff.append({
                'key': key,
                'type': 'removed',
                'value': value1,
            })
        elif is_dict(value1) and is_dict(value2):
            diff.append({
                'key': key,
                'type': 'nested',
                'children': build_diff(value1, value2),
            })
        elif value1 == value2:
            diff.append({
                'key': key,
                'type': 'unchanged',
                'value': value1,
            })
        else:
            diff.append({
                'key': key,
                'type': 'changed',
                'old_value': value1,
                'new_value': value2,
            })

    return diff

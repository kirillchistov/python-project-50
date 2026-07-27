from gendiff.parser import parse_file


def stringify(value):
    return str(value).lower() if isinstance(value, bool) else str(value)


def build_diff_lines(key, data1, data2):
    in_first = key in data1
    in_second = key in data2

    if in_first and in_second:
        if data1[key] == data2[key]:
            return [f'    {key}: {stringify(data1[key])}']
        return [
            f'  - {key}: {stringify(data1[key])}',
            f'  + {key}: {stringify(data2[key])}',
        ]
    if in_first:
        return [f'  - {key}: {stringify(data1[key])}']
    return [f'  + {key}: {stringify(data2[key])}']


def generate_diff(file_path1, file_path2):
    data1 = parse_file(file_path1)
    data2 = parse_file(file_path2)

    keys = sorted(data1.keys() | data2.keys())
    lines = [
        line
        for key in keys
        for line in build_diff_lines(key, data1, data2)
    ]
    return '{\n' + '\n'.join(lines) + '\n}'

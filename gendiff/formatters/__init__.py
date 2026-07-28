from gendiff.formatters.stylish import format_stylish


def format_diff(diff, format_name='stylish'):
    if format_name == 'stylish':
        return format_stylish(diff)
    raise ValueError(f'Unknown format: {format_name}')

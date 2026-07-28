INDENT_SIZE = 4


def to_string(value, depth):
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return 'null'
    if isinstance(value, dict):
        lines = ['{']
        current_indent = ' ' * (depth * INDENT_SIZE)
        closing_indent = ' ' * ((depth - 1) * INDENT_SIZE)
        for key in sorted(value.keys()):
            formatted_value = to_string(value[key], depth + 1)
            lines.append(f'{current_indent}{key}: {formatted_value}')
        lines.append(f'{closing_indent}}}')
        return '\n'.join(lines)
    return str(value)


def format_stylish(diff):
    def walk(nodes, depth):
        lines = []
        indent = ' ' * (depth * INDENT_SIZE - 2)

        for node in nodes:
            key = node['key']
            node_type = node['type']

            if node_type == 'nested':
                children = walk(node['children'], depth + 1)
                closing = ' ' * (depth * INDENT_SIZE)
                lines.append(f'{indent}  {key}: {{')
                lines.append(children)
                lines.append(f'{closing}}}')
            elif node_type == 'added':
                value = to_string(node['value'], depth + 1)
                lines.append(f'{indent}+ {key}: {value}')
            elif node_type == 'removed':
                value = to_string(node['value'], depth + 1)
                lines.append(f'{indent}- {key}: {value}')
            elif node_type == 'changed':
                old_value = to_string(node['old_value'], depth + 1)
                new_value = to_string(node['new_value'], depth + 1)
                lines.append(f'{indent}- {key}: {old_value}')
                lines.append(f'{indent}+ {key}: {new_value}')
            elif node_type == 'unchanged':
                value = to_string(node['value'], depth + 1)
                lines.append(f'{indent}  {key}: {value}')

        return '\n'.join(lines)

    return '{\n' + walk(diff, 1) + '\n}'

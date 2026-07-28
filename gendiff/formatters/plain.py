def format_value(value):
    if isinstance(value, dict):
        return '[complex value]'
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return 'null'
    if isinstance(value, str):
        return f"'{value}'"
    return str(value)


def format_plain(diff):
    def walk(nodes, path):
        lines = []

        for node in nodes:
            property_path = f'{path}.{node["key"]}' if path else node['key']
            node_type = node['type']

            if node_type == 'nested':
                lines.extend(walk(node['children'], property_path))
            elif node_type == 'added':
                value = format_value(node['value'])
                lines.append(
                    f"Property '{property_path}' was added with value: {value}"
                )
            elif node_type == 'removed':
                lines.append(f"Property '{property_path}' was removed")
            elif node_type == 'changed':
                old_value = format_value(node['old_value'])
                new_value = format_value(node['new_value'])
                lines.append(
                    f"Property '{property_path}' was updated. "
                    f'From {old_value} to {new_value}'
                )

        return lines

    return '\n'.join(walk(diff, ''))

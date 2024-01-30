import json


def stringify(data):
    return str(data).lower()


"""
Calculate differences:
1. Create 2 dictionaries from 2 given json files
2. Combine the 2 dictionaries into 1 for full list of keys
3. Sort the keys (ascending order)
4. Compare the values of correspondent keys in 2 dictionaries
5. If keys exist, values are equal, add the string (key:value) as is
6. If keys don't exist or the values are not equal, mark them with '+' / '-'
7. Join and return the result
"""


def generate_diff(file_1, file_2):
    dct_1 = json.load(open(file_1))
    dct_2 = json.load(open(file_2))
    result = []
    all_keys = list(set(list(dct_1) + list(dct_2)))
    for key in sorted(all_keys):
        value_1 = stringify(dct_1.get(key))
        value_2 = stringify(dct_2.get(key))
        if key in dct_1.keys() and key in dct_2.keys():
            if dct_1[key] == dct_2[key]:
                result.append(f'    {key}: {value_1}')
            else:
                result.append(f'  - {key}: {value_1}')
                result.append(f'  + {key}: {value_2}')
        elif key in dct_1.keys():
            result.append(f'  - {key}: {value_1}')
        elif key in dct_2.keys():
            result.append(f'  + {key}: {value_2}')
    return '{\n' + '\n'.join(result) + '\n}'

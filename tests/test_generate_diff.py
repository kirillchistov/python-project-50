from pathlib import Path

import pytest

from gendiff import generate_diff


def get_test_data_path(filename):
    return Path(__file__).parent / 'test_data' / filename


def read_file(filename):
    return get_test_data_path(filename).read_text()


@pytest.mark.parametrize(
    ('file1_name', 'file2_name'),
    [
        ('file1.json', 'file2.json'),
        ('file1.yml', 'file2.yml'),
        ('file1.yaml', 'file2.yaml'),
        ('file1.json', 'file2.yml'),
        ('file1.yml', 'file2.json'),
    ],
)
def test_generate_diff_flat_files(file1_name, file2_name):
    file1 = get_test_data_path(file1_name)
    file2 = get_test_data_path(file2_name)
    expected = read_file('result_stylish.txt').rstrip('\n')
    actual = generate_diff(file1, file2)

    assert actual == expected


@pytest.mark.parametrize(
    ('file1_name', 'file2_name'),
    [
        ('nested1.json', 'nested2.json'),
        ('nested1.yml', 'nested2.yml'),
        ('nested1.json', 'nested2.yml'),
        ('nested1.yml', 'nested2.json'),
    ],
)
def test_generate_diff_nested_files(file1_name, file2_name):
    file1 = get_test_data_path(file1_name)
    file2 = get_test_data_path(file2_name)
    expected = read_file('result_stylish_nested.txt').rstrip('\n')
    actual = generate_diff(file1, file2)

    assert actual == expected


def test_generate_diff_default_formatter_is_stylish():
    file1 = get_test_data_path('nested1.json')
    file2 = get_test_data_path('nested2.json')
    expected = read_file('result_stylish_nested.txt').rstrip('\n')

    assert generate_diff(file1, file2) == expected
    assert generate_diff(file1, file2, 'stylish') == expected


@pytest.mark.parametrize(
    ('file1_name', 'file2_name'),
    [
        ('nested1.json', 'nested2.json'),
        ('nested1.yml', 'nested2.yml'),
        ('nested1.json', 'nested2.yml'),
        ('nested1.yml', 'nested2.json'),
    ],
)
def test_generate_diff_plain(file1_name, file2_name):
    file1 = get_test_data_path(file1_name)
    file2 = get_test_data_path(file2_name)
    expected = read_file('result_plain.txt').rstrip('\n')
    actual = generate_diff(file1, file2, 'plain')

    assert actual == expected


@pytest.mark.parametrize(
    ('file1_name', 'file2_name'),
    [
        ('nested1.json', 'nested2.json'),
        ('nested1.yml', 'nested2.yml'),
    ],
)
def test_generate_diff_json(file1_name, file2_name):
    import json

    file1 = get_test_data_path(file1_name)
    file2 = get_test_data_path(file2_name)
    expected = read_file('result_json.txt').rstrip('\n')
    actual = generate_diff(file1, file2, 'json')

    assert actual == expected
    assert json.loads(actual) == json.loads(expected)

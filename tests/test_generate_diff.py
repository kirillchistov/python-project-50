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

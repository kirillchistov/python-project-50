from pathlib import Path

from gendiff import generate_diff


def get_test_data_path(filename):
    return Path(__file__).parent / 'test_data' / filename


def read_file(filename):
    return get_test_data_path(filename).read_text()


def test_generate_diff_flat_json():
    file1 = get_test_data_path('file1.json')
    file2 = get_test_data_path('file2.json')
    expected = read_file('result_stylish.txt').rstrip('\n')
    actual = generate_diff(file1, file2)

    assert actual == expected

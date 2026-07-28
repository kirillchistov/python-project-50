#!/usr/bin/env python3
import argparse

from gendiff import generate_diff


PROG = 'gendiff'
DESCRIPTION = 'Compares two configuration files and shows a difference.'


def parse_args():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
    )
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    parser.add_argument(
        '-f',
        '--format',
        default='stylish',
        help='set format of output',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(generate_diff(args.first_file, args.second_file, args.format))


if __name__ == '__main__':
    main()

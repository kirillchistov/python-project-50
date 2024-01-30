#!/usr/bin/env python3
from gendiff import generate_diff
import argparse


PROG = 'Gendiff CLI utility'
DESCRIPTION = 'Compares two configuration files and shows a difference.'
EPILOG = 'Thanks for checking in.'

parser = argparse.ArgumentParser(
    prog=PROG,
    description=DESCRIPTION,
    epilog=EPILOG)
parser.add_argument('first_file', type=str)
parser.add_argument('second_file', type=str)
parser.add_argument('-f', '--format', help='set format of output')
args = parser.parse_args()


def main():
    print(args.first_file, args.second_file)
    print(generate_diff(args.first_file, args.second_file))


if __name__ == '__main__':
    main()

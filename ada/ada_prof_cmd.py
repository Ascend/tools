# ADA Profiling data analysis command line
import os
import sys
import logging
import argparse
from ada import pdav2


def parse_args(str_args):
    parser = argparse.ArgumentParser(prog='ada-pa', description="Ascend Debugging Assistant - Profiling Analysis")
    parser.add_argument("input_file", help="input file path")
    parser.add_argument("-o", "--output", help="output file path")
    parser.add_argument("--reporter", action="append", help="Specify self-defined reporter, "
                                                            "and there should be a report function in the file")

    return parser.parse_args(str_args)


def init_log():
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger('hdfs.client').setLevel(logging.WARNING)


def main():
    init_log()
    args = parse_args(sys.argv[1:])
    if not os.path.isfile(args.input_file):
        print("ERROR: The input file {} does not exists".format(args.input_file))
        return
    if args.output is None:
        args.output = os.path.dirname(os.path.realpath(args.input_file))

    if not os.path.exists(args.output):
        print("ERROR: The output path {} does not exists".format(args.output))
        return
    if not os.path.isdir(args.output):
        print("ERROR: The output path {} is not a directory".format(args.output))
        return
    pure_name, _ = os.path.splitext(os.path.basename(args.input_file))
    args.output = os.path.join(args.output, pure_name)
    return pdav2.main_ge(args)


if __name__ == "__main__":
    main()

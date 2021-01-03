import argparse
import os
import sys

from .platform.ovio_core_platform import OvioCorePlatform
from .apps.pll_timer import PllTimer
from .apps.ft600_test import FT600_Test


def main():
    plat = OvioCorePlatform()
    # plat.build(PllTimer(), do_program=False)
    plat.build(FT600_Test(), do_program=False)

    # # Create the parser
    # my_parser = argparse.ArgumentParser(
    #     description='List the content of a folder')

    # my_parser.add_argument('Path',
    #                        metavar='path',
    #                        type=str,
    #                        help='the path to list')

    # # Execute the parse_args() method
    # args = my_parser.parse_args()

    # input_path = args.Path

    # if not os.path.isdir(input_path):
    #     print('The path specified does not exist')
    #     sys.exit()

    # print('\n'.join(os.listdir(input_path)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf8 -*-

""" Main file. If called with no command line arguments, starts the
command line user interface, otherwise tries to execute the command line
arguments as if they had been entered in the command line user interface.
"""

import os
import sys
import logging
import signal
from rtklookup.ui import LookupCli
from rtklookup.collection import KanjiCollection
from rtklookup.log import logger
from rtklookup.config import load_config
from rtklookup import handler
import argparse

def create_parser():
    parser = argparse.ArgumentParser(prog='rtk', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbosity')
    parser.add_argument('keywords', metavar='N', nargs='*', help='Keywords used to lookup')

    return parser

def main():
    signal.signal(signal.SIGINT, lambda signal, frame: handler.exit())
    args = create_parser().parse_args()

    # else the datafile will not be found if the script is called
    # from another location
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    if not args.verbose:
        if args.keywords:
            # not running with user interface: suppress warnings
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.WARNING)

    # do this after we have properly setup the logger
    load_config()

    kanji_collection = KanjiCollection()
    logger.debug("Loading rtk data...")
    kanji_collection._load_file_rtk()
    logger.debug("Loading stories...")
    kanji_collection.load_file_stories()
    logger.debug("Loading done.")

    if not args.keywords:
        # No argument given > start cli interface
        LookupCli(kanji_collection).cmdloop()
    else:
        # future: add option to generate better parsable output
        cli = LookupCli(kanji_collection)
        for keyword in args.keywords:
            # else it matters whether there is a space in front of the ',':
            keyword = keyword.lstrip()
            if not keyword.startswith('.'):
                print("Output for '%s':" % keyword)
            cli.default(keyword)


if __name__ == '__main__':
    main()

#!/usr/bin/python3
# -*- coding: utf8 -*-

""" Main file. If called with no command line arguments, starts the
command line user interface, otherwise tries to execute the command line
arguments as if they had been entered in the command line user interface.
"""

import os
import sys
import logging
from rtklookup.ui import LookupCli
from rtklookup.collection import KanjiCollection
from rtklookup.log import logger
from rtklookup.colorama import colorama
from rtklookup.config import load_config

__author__ = "klieret"
__license__ = "LGPLv3"

if __name__ == '__main__':

    # else the datafile will not be found if the script is called
    # from another location
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # logger was set up before by log, but we didn't have
    # coloring at that time. Now we (might) have it, in which case
    # we reset the formatter.
    if colorama:
        sh = logger.handlers[0]
        fm = logging.Formatter(colorama.Style.DIM +
                               "%(levelname)s: %(message)s" +
                               colorama.Style.RESET_ALL)
        sh.setFormatter(fm)

    if not len(sys.argv) == 1:
        # not running with user interface: suppress warnings
        logger.setLevel(logging.CRITICAL)

    # do this after we have properly setup the logger
    load_config()

    kanji_collection = KanjiCollection()
    logger.debug("Loading rtk data...")
    kanji_collection._load_file_rtk()
    logger.debug("Loading stories...")
    kanji_collection.load_file_stories()
    logger.debug("Loading done.")

    if len(sys.argv) == 1:
        # No argument given > start cli interface
        LookupCli(kanji_collection).cmdloop()

    else:
        # future: add option to generate better parsable output
        lines = ' '.join(sys.argv[1:]).split(";")
        cli = LookupCli(kanji_collection)
        for l in lines:
            # else it matters whether there is a space in front of the ',':
            l = l.lstrip()
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)

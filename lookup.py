#!/usr/bin/python3
# -*- coding: utf8 -*-

"""
Lookup Kanji by Heisig Keyword or frame number
----------------------------------------------

See https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword.git
for more information.

**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU GPL, version 3 or later

About This File
---------------

The main file. 
Run it with
    
    python3 lookup.py

or (under linux, after ```chmod +x lookup.py```)

    ./lookup.py
"""

import os
import sys
from ui import LookupCli
from collection import KanjiCollection
from log import logger
import logging
from _colorama import colorama

if __name__ == '__main__':

    # else the datafile will not be found if the script is called
    # from another location
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # logger was set up before by log, but we didn't have
    # coloring at that time. Now we (might) have it, in which case
    # we reset the formatter.
    if colorama:
        sh = logger.handlers[0]
        fm = logging.Formatter(colorama.Style.DIM + "%(levelname)s: %(message)s" + colorama.Style.RESET_ALL)
        sh.setFormatter(fm)

    if not len(sys.argv) == 1:
        # not running with user interface: suppress warnings
        logger.setLevel(logging.CRITICAL)

    kanji_collection = KanjiCollection()
    logger.debug("Loading rtk data...")
    kanji_collection.load_file_rtk()
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
            l = l.lstrip()  # else it matters whether there is a space in front of the ','
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)

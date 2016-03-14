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
import logging

from collection import *
from ui import *
from modules import *

global logger
global colorama


if __name__ == '__main__':

    # else the datafile will not be found if the script is called
    # from another location
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    logger = logging.getLogger("lookup")
    
    # remove previous handler
    logger.handlers = []
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    fm = logging.Formatter(colorama.Style.DIM + "%(levelname)s: %(message)s" + colorama.Style.RESET_ALL)
    sh.setFormatter(fm)
    logger.addHandler(sh)

    # >>>>>> Load Data
    kc = KanjiCollection()
    logger.debug("Loading rtk data...")
    kc.update_rtk()
    logger.debug("Loding stories...")
    kc.update_stories()
    logger.debug("Loading done.")
    
    if len(sys.argv) == 1:
        # No argument given > start cli interface
        LookupCli(kc).cmdloop()
    
    else:
        # There were arguments > look them up
        logger.setLevel(logging.CRITICAL)
        lines = ' '.join(sys.argv[1:]).split(",")
        cli = LookupCli(kc)
        for l in lines:
            l = l.lstrip()    # else it matters whether there is a space in front of the ','
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)

#!/usr/bin/python3
# -*- coding: utf8 -*-

""" Quickly sets up a log.
"""

import logging
import colorama


logger = logging.getLogger("lookup")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fm = logging.Formatter(colorama.Style.DIM + "%(levelname)s: %(message)s" +
                       colorama.Style.RESET_ALL)
sh.setFormatter(fm)
logger.addHandler(sh)

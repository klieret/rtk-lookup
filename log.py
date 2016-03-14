#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging

# Note: Will get partially redefined in lookup.py

logger = logging.getLogger("lookup")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fm = logging.Formatter("%(levelname)s: %(message)s")
sh.setFormatter(fm)
logger.addHandler(sh)
logger.addHandler(sh)
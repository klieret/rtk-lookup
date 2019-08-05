#!/usr/bin/python3
# -*- coding: utf8 -*-

""" Quickly sets up a log.
"""

import colorlog
import logging


logger = colorlog.getLogger("lookup")
logger.setLevel(logging.DEBUG)
sh = colorlog.StreamHandler()
sh.setLevel(logging.DEBUG)
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}
fm = colorlog.ColoredFormatter(
    "%(log_color)s%(name)s:%(levelname)s:%(message)s",
    log_colors=log_colors,
)
sh.setFormatter(fm)
logger.addHandler(sh)

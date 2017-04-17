#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os.path
from .log import logger


config = configparser.ConfigParser()
# allow dynamic stuff:
config._interpolation = configparser.ExtendedInterpolation()
config_files = ["config/default.config"]


def load_config():
    logger.info("Loading configuration from the following file(s): %s." %
                ', '.join(config_files))
    for cfile in config_files:
        if not os.path.exists(cfile):
            logger.warning("Couldn't find config file {}".format(
                os.path.abspath(cfile)))
    config.read(config_files)

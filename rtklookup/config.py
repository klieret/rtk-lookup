#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os.path
from rtklookup.log import logger
from pkg_resources import resource_filename


config = configparser.ConfigParser()
# allow dynamic stuff:
config._interpolation = configparser.ExtendedInterpolation()
config_files = [resource_filename('rtklookup', 'config/default.config')]


def load_config():
    logger.info("Loading configuration from the following file(s): %s." %
                ', '.join(config_files))
    for cfile in config_files:
        if not os.path.exists(cfile):
            logger.warning("Couldn't find config file {}".format(
                os.path.abspath(cfile)))
    config.read(config_files)

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

Try to import the romkan and colorama module.
If the latter fails, define an "empty copy" of it, so 
that we don't have to care about it in the other modules.
"""

import logging

global logger
global colorama

# have to predefine logger here
# to log errors with colorama etc.
# later (in __main__) the stream handler gets redefined

logger = logging.getLogger("lookup")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
fm = logging.Formatter("%(levelname)s: %(message)s")
sh.setFormatter(fm)
logger.addHandler(sh)
logger.addHandler(sh)

# The 'romkan' module is used to convert hiragana to romanji (optional).
# It is available at https://pypi.python.org/pypi/romkan
try:
    import romkan
except ImportError:
    romkan = None
    logger.warning("Romkan module not found. No Support for hiragana.")
    logger.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")

# The 'colorama' module is  used to display colors in a platform independent way (optional). 
# It is available at https://pypi.python.org/pypi/colorama

# In case we don't have colorama, we simply define a mock class
from collections import namedtuple
class coloramaOverride(object):
    def __init__(self):
        self.Fore = namedtuple("Fore", "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE RESET")
        self.Back = namedtuple("Back", "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE RESET")
        self.Style = namedtuple("Style", "DIM NORMAL BRIGHT RESET_ALL")
        self.unset()
    def unset(self):
        self.Fore.BLACK = ""
        self.Fore.RED = ""
        self.Fore.GREEN = ""
        self.Fore.YELLOW = ""
        self.Fore.BLUE = ""
        self.Fore.MAGENTA = ""
        self.Fore.CYAN = ""
        self.Fore.WHITE = ""
        self.Fore.RESET = ""
        self.Back.BLACK = ""
        self.Back.RED = ""
        self.Back.GREEN = ""
        self.Back.YELLOW = ""
        self.Back.BLUE = ""
        self.Back.MAGENTA = ""
        self.Back.CYAN = ""
        self.Back.WHITE = ""
        self.Back.RESET = ""
        self.Style.DIM = ""
        self.Style.NORMAL = ""
        self.Style.BRIGHT = ""
        self.Style.RESET_ALL = ""

colorama = coloramaOverride()
try:
    import colorama
except ImportError:
    logger.warning("Colorama module not found. No Support for colors.")
    logger.debug("Colorama is available at https://pypi.python.org/pypi/colorama.")
else:
    colorama.init()

def removeColor(string):
    string = string.replace(colorama.Fore.BLACK, "")
    string = string.replace(colorama.Fore.RED, "")
    string = string.replace(colorama.Fore.GREEN, "")
    string = string.replace(colorama.Fore.YELLOW, "")
    string = string.replace(colorama.Fore.BLUE, "")
    string = string.replace(colorama.Fore.MAGENTA, "")
    string = string.replace(colorama.Fore.CYAN, "")
    string = string.replace(colorama.Fore.WHITE, "")
    string = string.replace(colorama.Fore.RESET, "")
    string = string.replace(colorama.Back.BLACK, "")
    string = string.replace(colorama.Back.RED, "")
    string = string.replace(colorama.Back.GREEN, "")
    string = string.replace(colorama.Back.YELLOW, "")
    string = string.replace(colorama.Back.BLUE, "")
    string = string.replace(colorama.Back.MAGENTA, "")
    string = string.replace(colorama.Back.CYAN, "")
    string = string.replace(colorama.Back.WHITE, "")
    string = string.replace(colorama.Back.RESET, "")
    string = string.replace(colorama.Style.DIM, "")
    string = string.replace(colorama.Style.NORMAL, "")
    string = string.replace(colorama.Style.BRIGHT, "")
    string = string.replace(colorama.Style.RESET_ALL, "")
    return string

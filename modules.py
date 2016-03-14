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
try:
    import colorama
except ImportError:
    colorama = None
    logger.warning("Colorama module not found. No Support for colors.")
    logger.debug("Colorama is available at https://pypi.python.org/pypi/colorama.")
else:
    colorama.init()


def remove_color(string: str) -> str:
    """ Removes all formatting from input. Useful for
    getting the length of a string.
    :param string:
    :return:
    """
    if not colorama:
        return

    colors = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET", "BLACK", "RED", "GREEN",
              "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET", ]
    styles = ["DIM", "NORMAL", "BRIGHT", "RESET_ALL"]

    for color in colors:
        string = string.replace(getattr(colorama.Fore, color), "")
        string = string.replace(getattr(colorama.Back, color), "")
    for style in styles:
        string = string.replace(getattr(colorama.Style, style), "")

    return string

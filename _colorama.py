#!/usr/bin/python3
# -*- coding: utf8 -*-

from log import logger

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
    """ Removes all formatting (i.e. escape sequences) from input string.
    Useful for getting the display length of a string. Only works if colorama
    module is installed (and imported).
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
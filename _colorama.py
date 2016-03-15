#!/usr/bin/python3
# -*- coding: utf8 -*-

from log import logger
import re

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


if colorama:
    color_name_list = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET", "BLACK", "RED",
                       "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET", ]
    style_name_list = ["DIM", "NORMAL", "BRIGHT", "RESET_ALL"]

    fore_color_list = [getattr(colorama.Fore, color) for color in color_name_list]
    back_color_list = [getattr(colorama.Back, color) for color in color_name_list]
    style_list = [getattr(colorama.Style, style) for style in style_name_list]
    formatting_sequence_list = fore_color_list + back_color_list + style_list

    escaped_formatting_sequence_list = [re.escape(item) for item in formatting_sequence_list]
    _regex_string = '|'.join(escaped_formatting_sequence_list + [".?"])
    formatting_sequence_regex = re.compile('|'.join(escaped_formatting_sequence_list + [".+"]))


def remove_color(string: str) -> str:
    """ Removes all formatting (i.e. escape sequences) from input string.
    Useful for getting the display length of a string. Only works if colorama
    module is installed (and imported).
    :param string:
    :return:
    """
    if not colorama:
        return

    for formatter in formatting_sequence_list:
        string = string.replace(formatter, "")

    return string


def split_colors(string: str):
    return formatting_sequence_regex.findall(string)


def strip_leading(string: str, trailing: str) -> str:
    split = split_colors(string)
    for i, s in enumerate(split):
        if s not in formatting_sequence_list and s.startswith(trailing):
            split[i] = s[len(trailing):]
            break
    return ''.join(split)


def strip_trailing(string: str, trailing: str) -> str:
    split = split_colors(string)
    for i, s in enumerate(reversed(split)):
        if s not in formatting_sequence_list and s.endswith(trailing):
            split[len(split) - 1 - i] = s[:-len(trailing)]
            break
    return ''.join(split)


# todo: Make into ColorString class later

# print(strip_trailing(colorama.Fore.RED + "test", "t"))

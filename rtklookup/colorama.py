#!/usr/bin/python3
# -*- coding: utf8 -*-

""" Tries to import the colorama module, otherwise defines colorama = None.
Also defines function to help with color related issues.
"""

import re
import colorama
colorama.init()


def remove_color(string: str) -> str:
    """ Removes all formatting (i.e. escape sequences) from input string.
    Useful for getting the display length of a string.
    If colorama is not installed, returns string as it is.
    :param string: string possibly containing colorama formatting sequences.
    :return:
    """

    # todo: can't I just remove all escape sequenes?
    # or will that not work on windows?
    # 1. get all formatting sequences
    color_name_list = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA",
                       "CYAN", "WHITE", "RESET", "BLACK", "RED", "GREEN",
                       "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "RESET", ]
    style_name_list = ["DIM", "NORMAL", "BRIGHT", "RESET_ALL"]

    fore_color_list = \
        [getattr(colorama.Fore, color) for color in color_name_list]
    back_color_list = \
        [getattr(colorama.Back, color) for color in color_name_list]
    style_list = [getattr(colorama.Style, style) for style in style_name_list]

    formatting_sequence_list = fore_color_list + back_color_list + style_list

    # 2. escape them and build a regular expression that searches for
    # everything but them
    escaped_formatting_sequence_list = \
        [re.escape(item) for item in formatting_sequence_list]
    not_formatting_sequence_regex = \
        re.compile("[^{}]".format(''.join(escaped_formatting_sequence_list)))

    # 3. join the search results and return
    return ''.join(not_formatting_sequence_regex.findall(string))

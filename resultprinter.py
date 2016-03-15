#!/usr/bin/python3
# -*- coding: utf8 -*-

from typing import List
from searchresults import SearchGroupCollection, SearchGroup
from util import CyclicalList, approximate_string_length
from collections import namedtuple
from _colorama import colorama, remove_color


class ResultPrinter(object):
    """ Class used to print the result of a query made by the user.
    """
    def __init__(self, search_group_collection: SearchGroupCollection):
        """
        :param search_group_collection: SearchItemCollection object containing the information about the search results.
        :return:None
        """
        self.group_collection = search_group_collection

        self._colors = None
        self._setup_color_set()  # sets self.colors

        self._first_line = ""
        self._details = ""
        self._first_line_groups = []  # type: List[str]
        self._detail_groups = []  # type: List[List[str]]

        self._indent_all = 4

    def _setup_color_set(self):
        """ Sets up the namedtuple self.colors that holds the color settings.
        :return:
        """
        _colors_type = namedtuple("colors", ["kanji", "kana", "broken",  "default"])
        if colorama:
            self._colors = _colors_type(kanji=CyclicalList([colorama.Fore.RED, colorama.Fore.BLUE]),
                                        kana=CyclicalList([colorama.Fore.CYAN]),
                                        broken=CyclicalList([colorama.Fore.YELLOW]),
                                        default=colorama.Style.RESET_ALL)
        else:
            # everything will be black...
            self._colors = _colors_type(kanji=CyclicalList([""]),
                                        kana=CyclicalList([""]),
                                        broken=CyclicalList([""]),
                                        default="")

    # noinspection PyUnusedLocal
    def _group_color(self, group: SearchGroup, item="") -> str:
        """Cyclical colors for the different SearchGroups
        :param group:
        :param item: For polymorphism with self.item_color. Has no effect.
        :return: Color as escape sequence.
        """
        return getattr(self._colors, group.type)[self._nth_group_of_type(group)]

    def _item_color(self, group: SearchGroup, item="") -> str:
        """Cyclical colors for items inside of one SearchGroup
        :param group:
        :param item:
        :return:
        """
        if group.type == "kanji":
            return getattr(self._colors, group.type)[group.kanji.index(item)]
        else:
            return getattr(self._colors, group.type)[0]  # there's only one

    def _nth_group_of_type(self, group: SearchGroup) -> int:
        """ Position of SearchGroup among the other SearchGroups of same type in
        the SearchGroupCollection.
        :param group:
        :return:
        """
        nth = 0
        for other in self.group_collection:
            if group == other:
                return nth
            if group.type == other.type:
                nth += 1

    def _format_first_line(self):
        """ Format the first line. First line will be empty if not nescessary. """
        if self.group_collection.is_empty:
            self._first_line = "Empty search."
            return
        if not self.group_collection.multiple_searches and not self.group_collection.is_unique:
            # first line unnescessary, leave it empty
            return
        for group in self.group_collection.groups:
            if group.is_empty:
                continue
            if group.has_kanji:
                group_string = ""
                for kanji in group.kanji:
                    group_string += self._group_color(group) + kanji.kanji + self._colors.default
                self._first_line_groups.append(group_string)
            elif group.has_kana:
                self._first_line_groups.append(self._group_color(group) + group.hiragana +
                                               self._colors.default)
            elif group.is_broken:
                self._first_line_groups.append(self._group_color(group) + group.search + self._colors.default)
            else:
                raise ValueError

        # if group length > 1 add symbols
        self._first_line = ''.join(self._first_line_groups)

    def _format_details(self):
        """ Format the detail block. Detail block will be empty if not requred. """
        if self.group_collection.multiple_searches:
            colorer = self._group_color  # color by group: every group has one color
        else:
            colorer = self._item_color  # color by item: every kanji inside a group has one color

        for group in self.group_collection.groups:
            if group.has_kanji and group.is_unique:
                details = []
                for kanji in group.kanji:
                    details.append("{}{}: {}{}".format(colorer(group, item=kanji), kanji.kanji, kanji.meaning,
                                                       self._colors.default))
                self._detail_groups.append(details)

    def _print_line(self, line: str):
        """ Wrapper around normal print() function to implement indenting and such.
        :param line:
        """
        print(" " * self._indent_all + line)

    def _print_divider(self, char: str):
        """ Prints dividing line.
        :param char: The character/string used.
        :return:
        """
        divider = char * approximate_string_length(self._first_line)
        self._print_line(divider)

    def print(self):
        """ Print the result. "Main" function.
        :return:
        """
        print()
        self._format_first_line()
        self._format_details()
        self._print_first_line()
        if remove_color(self._first_line) and self._detail_groups:
            self._print_divider("\u2500")
        self._print_details()
        print()

    def _print_first_line(self):
        """Print first line. """
        self._print_line(self._first_line)

    def _print_details(self):
        """ Print details block. """
        for group_no, group in enumerate(self._detail_groups):
            for item in group:
                self._print_line(item)
            if not group_no == len(self._detail_groups)-1:
                self._print_divider("\u2508")

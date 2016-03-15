#!/usr/bin/python3
# -*- coding: utf8 -*-

from typing import List
from searchresults import SearchResult, SearchResultGroup
from util import CyclicalList, approximate_string_length
from collections import namedtuple
from _colorama import colorama, remove_color


class ResultPrinter(object):
    """ Class used to print the result of a query made by the user. """
    def __init__(self, search_group_collection: SearchResult):
        """
        :param search_group_collection: SearchItemCollection object containing the information about the search results.
        :return:None
        """
        self.result = search_group_collection

        self.colors = None
        self.setup_color_set()  # sets self.colors

        self.first_line = ""
        self.details = ""
        self.first_line_groups = []  # type: List[str]
        self.detail_groups = []  # type: List[List[str]]

        self._indent_all = 4

    def setup_color_set(self):
        """ Sets up the namedtuple self.colors that holds the color settings.
        :return:
        """
        _colors_type = namedtuple("colors", ["kanji", "kana", "broken",  "default"])
        if colorama:
            self.colors = _colors_type(kanji=CyclicalList([colorama.Fore.RED, colorama.Fore.BLUE]),
                                       kana=CyclicalList([colorama.Fore.CYAN]),
                                       broken=CyclicalList([colorama.Fore.YELLOW]),
                                       default=colorama.Style.RESET_ALL)
        else:
            # everything will be black...
            self.colors = _colors_type(kanji=CyclicalList([""]),
                                       kana=CyclicalList([""]),
                                       broken=CyclicalList([""]),
                                       default="")

    # noinspection PyUnusedLocal
    def group_color(self, group: SearchResultGroup, item="") -> str:
        """Cyclical colors for the different SearchGroups
        :param group:
        :param item: For polymorphism with self.item_color. Has no effect.
        :return: Color as escape sequence.
        """
        return getattr(self.colors, group.type)[self.nth_group_of_type(group)]

    def item_color(self, group: SearchResultGroup, item="") -> str:
        """Cyclical colors for items inside of one SearchGroup
        :param group:
        :param item:
        :return:
        """
        if group.type == "kanji":
            return getattr(self.colors, group.type)[group.kanji.index(item)]
        else:
            return getattr(self.colors, group.type)[0]  # there's only one

    def nth_group_of_type(self, group: SearchResultGroup) -> int:
        """ Position of SearchGroup among the other SearchGroups of same type in
        the SearchGroupCollection.
        :param group:
        :return:
        """
        nth = 0
        for other in self.result:
            if group == other:
                return nth
            if group.type == other.type:
                nth += 1

    def format_first_line(self):
        """ Format the first line. First line will be empty if not necessary. """
        if self.result.is_empty:
            self.first_line = "Empty search."
            return
        if not self.result.multiple_searches and not self.result.is_unique:
            # first line unnecessary, leave it empty
            return
        for group in self.result.groups:
            if group.is_empty:
                continue
            if group.has_kanji:
                group_string = ""
                for kanji in group.kanji:
                    group_string += self.group_color(group) + kanji.kanji + self.colors.default
                self.first_line_groups.append(group_string)
            elif group.is_kana:
                self.first_line_groups.append(self.group_color(group) + group.kana +
                                              self.colors.default)
            elif group.is_broken:
                self.first_line_groups.append(self.group_color(group) + group.search_general + self.colors.default)
            else:
                raise ValueError

        # if group length > 1 add symbols
        self.first_line = ''.join(self.first_line_groups)

    def format_details(self):
        """ Format the detail block. Detail block will be empty if not requred. """
        if self.result.multiple_searches:
            colorer = self.group_color  # color by group: every group has one color
        else:
            colorer = self.item_color  # color by item: every kanji inside a group has one color

        for group in self.result.groups:
            if group.has_kanji and not group.is_unique:
                details = []
                for kanji in group.kanji:
                    details.append("{}{}: {}{}".format(colorer(group, item=kanji), kanji.kanji, kanji.meaning,
                                                       self.colors.default))
                self.detail_groups.append(details)

    def print_line(self, line: str):
        """ Wrapper around normal print() function to implement indenting and such.
        :param line:
        """
        print(" " * self._indent_all + line)

    def print_divider(self, char: str):
        """ Prints dividing line.
        :param char: The character/string used.
        :return:
        """
        divider = char * approximate_string_length(self.first_line)
        self.print_line(divider)

    def print(self):
        """ Print the result. "Main" function.
        :return:
        """
        print()
        self.format_first_line()
        self.format_details()
        self.print_first_line()
        if remove_color(self.first_line) and self.detail_groups:
            self.print_divider("\u2500")
        self.print_details()
        print()

    def print_first_line(self):
        """Print first line. """
        if self.first_line:
            # if needed to avoid line break if self.first_line is empty
            self.print_line(self.first_line)

    def print_details(self):
        """ Print details block. """
        for group_no, group in enumerate(self.detail_groups):
            for item in group:
                self.print_line(item)
            if not group_no == len(self.detail_groups)-1:
                self.print_divider("\u2508")

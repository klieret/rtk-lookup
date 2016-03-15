#!/usr/bin/python3
# -*- coding: utf8 -*-

from typing import List
import re
from searchresults import SearchGroupCollection, SearchGroup
from util import CyclicalList
from collections import namedtuple
from _colorama import colorama, remove_color


class ResultPrinter(object):
    def __init__(self, search_group_collection: SearchGroupCollection):
        """
        :param search_group_collection: SearchItemCollection object containing the information about the search results.
        :return:None
        """
        self.group_collection = search_group_collection

        self.colors = None
        self.setup_color_set()  # sets self.colors

        self.first_line = ""
        self.details = ""
        self.first_line_groups = []  # type: List[str]
        self.detail_groups = []  # type: List[List[str]]

        self.indent_all = 4
        self.indent_details = 0

    def setup_color_set(self):
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

    def group_color(self, group: SearchGroup, item="") -> str:
        return getattr(self.colors, group.type)[self.nth_group_of_type(group)]

    def item_color(self, group: SearchGroup, item="") -> str:
        if group.type == "kanji":
            return getattr(self.colors, group.type)[group.kanji.index(item)]
        else:
            return getattr(self.colors, group.type)[0]  # there's only one

    def nth_group_of_type(self, group: SearchGroup) -> int:
        nth = 0
        for other in self.group_collection:
            if group == other:
                return nth
            if group.type == other.type:
                nth += 1

    def format_first_line(self):
        if self.group_collection.is_empty:
            self.first_line = "Empty search."
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
                    group_string += self.group_color(group) + kanji.kanji + self.colors.default
                self.first_line_groups.append(group_string)
            elif group.has_kana:
                self.first_line_groups.append(self.group_color(group) + group.hiragana +
                                              self.colors.default)
            elif group.is_broken:
                self.first_line_groups.append(self.group_color(group) + group.search + self.colors.default)
            else:
                raise ValueError

        # if group length > 1 add symbols
        self.first_line = ''.join(self.first_line_groups)

    def format_details(self):
        if self.group_collection.is_unique:
            return
        if self.group_collection.multiple_searches:
            colorer = self.group_color
        else:
            colorer = self.item_color

        for group in self.group_collection.groups:
            if not group.is_unique:
                details = []
                for kanji in group.kanji:
                    details.append("{}{}: {}{}".format(colorer(group, item=kanji), kanji.kanji, kanji.meaning,
                                                       self.colors.default))
                self.detail_groups.append(details)

    @staticmethod
    def approximate_string_length(string: str) -> int:
        """ Note that kanji have about twice the width of European
        characters. This Function returns the length of $string as a
        multiple of the length of a European character.
        :param string: String.
        :return:
        """
        string = remove_color(string)
        latin_chars_regex = re.compile("[\u0020-\u007f]")
        return 2*len(string) - len(latin_chars_regex.findall(string))

    def print(self):
        print()
        self.format_first_line()
        self.format_details()
        self.print_first_line()
        if remove_color(self.first_line) and self.detail_groups:
            main_divider = "\u2500"*self.approximate_string_length(self.first_line)
            print(" "*self.indent_all + main_divider)
        self.print_details()
        print()

    def print_first_line(self):
        if remove_color(self.first_line):
            print(" "*self.indent_all + self.first_line)

    def print_details(self):
        details_subdevider = "\u2508"*self.approximate_string_length(self.first_line)
        for no, group in enumerate(self.detail_groups):
            for result in group:
                print(" "*(self.indent_all+self.indent_details) + result)
            if not no == len(self.detail_groups)-1:
                print(" "*(self.indent_all+self.indent_details) + details_subdevider)

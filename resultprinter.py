#!/usr/bin/python3
# -*- coding: utf8 -*-

from typing import List
import re
from searchresults import SearchGroupCollection, SearchGroup
from util import CyclicalList
from collections import namedtuple
from _colorama import colorama, remove_color


class ResultPrinter(object):
    def __init__(self, search_item_collection: SearchGroupCollection):
        """
        :param search_item_collection: SearchItemCollection object containing the information about the search results.
        :return:None
        """
        self.group_collection = search_item_collection

        _colors_type = namedtuple("colors", ["kanji", "kana", "broken",  "default"])

        if colorama:
            self.colors = _colors_type(kanji=CyclicalList([colorama.Fore.RED, colorama.Fore.BLUE]),
                                       kana=CyclicalList([colorama.Fore.CYAN]),
                                       broken=CyclicalList([colorama.Fore.YELLOW]),
                                       default=colorama.Style.RESET_ALL)
        else:
            self.colors = _colors_type(kanji=CyclicalList([""]),
                                       kana=CyclicalList([""]),
                                       broken=CyclicalList([""]),
                                       default="")

        self.first_line = ""
        self.details = ""
        self.first_line_groups = []  # type: List[str]
        self.detail_groups = []  # type: List[List[str]]

        self.indent_all = 4
        self.indent_details = 0

    def format_first_line(self):
        if self.group_collection.is_empty:
            self.first_line = "Empty search."
            return
        if not self.group_collection.multiple_searches and not self.group_collection.is_unique:
            # first line unnescessary, leave it empty
            return
        for search_item_no, search_item in enumerate(self.group_collection.items):
            if search_item.is_empty:
                continue
            if search_item.has_kanji:
                group = ""
                for kanji in search_item.kanji:
                    group += self.group_color(search_item) + kanji.kanji + self.colors.default
                self.first_line_groups.append(group)
            elif search_item.has_kana:
                self.first_line_groups.append(self.group_color(search_item) + search_item.hiragana +
                                              self.colors.default)
            elif search_item.is_broken:
                self.first_line_groups.append(self.group_color(search_item) + search_item.search + self.colors.default)
            else:
                raise ValueError

        # if group length > 1 add symbols
        self.first_line = ''.join(self.first_line_groups)

    def nth_item_of_type(self, item: SearchGroup) -> int:
        nth = 0
        for other in self.group_collection:
            if item == other:
                return nth
            if item.type == other.type:
                nth += 1

    def group_color(self, item: SearchGroup) -> str:
        return getattr(self.colors, item.type)[self.nth_item_of_type(item)]

    def atom_color(self, atom: str, item: SearchGroup) -> str:
        if item.type == "kanji":
            return getattr(self.colors, item.type)[item.kanji.index(atom)]
        else:
            return getattr(self.colors, item.type)[0]  # there's only one

    def fromat_detail_items(self):
        # print(self.search_results.is_broken, self.search_results.multiple_searches, self.search_results.is_unique)
        if self.group_collection.is_unique:
            return
        if self.group_collection.multiple_searches:
            self.format_details_multiple_groups()
        else:
            self.format_details_single_group()

    def format_details_single_group(self):
        details = []
        search_item = self.group_collection.items[0]
        if search_item.has_kanji:
            for no, kanji in enumerate(search_item.kanji):
                details.append("{}{}: {}{}".format(self.atom_color(kanji, search_item), kanji.kanji, kanji.meaning,
                                                   self.colors.default))
        else:
            # shouldn't happen. everything else should be unique
            raise ValueError
        self.detail_groups.append(details)

    def format_details_multiple_groups(self):
        for item in self.group_collection:
            if not item.is_unique:
                details = []
                for kanji in item.kanji:
                    # same coloring as the groups
                    details.append("{}{}: {}{}".format(self.group_color(item), kanji.kanji, kanji.meaning,
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

    def print_details(self):
        details_subdevider = "\u2508"*self.approximate_string_length(self.first_line)
        for no, group in enumerate(self.detail_groups):
            for result in group:
                print(" "*(self.indent_all+self.indent_details) + result)
            if not no == len(self.detail_groups)-1:
                print(" "*(self.indent_all+self.indent_details) + details_subdevider)

    def print_first_line(self):
        if remove_color(self.first_line):
            print(" "*self.indent_all + self.first_line)

    def print(self):
        print()
        self.format_first_line()
        self.fromat_detail_items()
        self.print_first_line()
        if remove_color(self.first_line) and self.detail_groups:
            main_divider = "\u2500"*self.approximate_string_length(self.first_line)
            print(" "*self.indent_all + main_divider)
        self.print_details()
        print()

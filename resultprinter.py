#!/usr/bin/python3
# -*- coding: utf8 -*-

from modules import colorama, remove_color
from collection import Kanji
from searchresults import SearchItemCollection, SearchItem


class CyclicalList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def __getitem__(self, item):
        return list.__getitem__(self, item % len(self))


class ResultPrinter(object):
    def __init__(self, search_item_collection: SearchItemCollection, force_annotation=False):
        """
        :param
        :return:None
        """
        self.force_annotation = force_annotation
        self.search_results = search_item_collection

        if colorama:
            self.kanji_colors = CyclicalList([colorama.Fore.RED, colorama.Fore.BLUE])
            self.kana_colors = CyclicalList([colorama.Fore.CYAN])
            self.not_found_colors = CyclicalList([colorama.Fore.YELLOW])
            self.default_color = colorama.Style.RESET_ALL
        else:
            # colorama not installed
            self.kanji_colors = [""]
            self.kana_colors = [""]
            self.not_found_colors = [""]
            self.default_color = ""

        self.color_by_type = {"kanji": self.kanji_colors, "kana": self.kana_colors, "broken": self.not_found_colors}


        self.first_line = self.default_color
        self.detail_groups = []  # type: list[list[str]]

        self.indent_all = 4
        self.indent_details = 0

    def format_first_line(self):
        if not self.search_results.multiple_searches and not self.search_results.is_unique:
            # first line unnescessary, leave it empty
            return
        for search_item_no, search_item in enumerate(self.search_results.items):
            if search_item.is_empty:
                continue
            if search_item.has_kanji:
                if not search_item.is_unique:
                    self.first_line += "("
                for kanji in search_item.kanji:
                    self.first_line += self.group_color(search_item) + kanji.kanji + self.default_color
                if not search_item.is_unique:
                    self.first_line += ")"
            elif search_item.has_kana:
                self.first_line += self.group_color(search_item) + search_item.hiragana + self.default_color
            elif search_item.is_failed:
                self.first_line += self.group_color(search_item) + search_item.search + self.default_color
            else:
                raise ValueError

    def nth_item_of_type(self, item: SearchItem) -> int:
        nth = 0
        for other in self.search_results:
            if item == other:
                return nth
            if item.type == other.type:
                nth += 1

    def group_color(self, item: SearchItem) -> str:
        return self.color_by_type[item.type][self.nth_item_of_type(item)]

    def format_details(self):
        if not self.search_results.multiple_searches and not self.search_results.is_unique:
            self.format_details_single_group()
        elif self.search_results.multiple_searches:
            self.format_details_multiple_groups()
        else:
            return

    def format_details_single_group(self):
        details = []
        search_item = self.search_results.items[0]
        if search_item.has_kanji:
            for no, kanji in enumerate(search_item.kanji):
                details.append("{}{}: {}{}".format(self.kanji_colors[no], kanji.kanji, kanji.meaning,
                                                   self.default_color))
        else:
            # shouldn't happen. everything else should be unique
            raise ValueError
        self.detail_groups.append(details)

    def format_details_multiple_groups(self):
        for item in self.search_results:
            if not item.is_unique:
                assert item.has_kanji
                details = []
                for kanji in item.kanji:
                    # same coloring as the groups
                    details.append("{}{}: {}{}".format(self.group_color(item), kanji.kanji, kanji.meaning,
                                                       self.default_color))
                self.detail_groups.append(details)

    @staticmethod
    def approximate_string_length(string):
        # works as long as there are no European characters
        # todo: also take european characters into account
        string = remove_color(string)
        brackets = string.count("(") + string.count(")")
        return 2*len(string) - brackets

    def print(self):
        print()
        if self.search_results.is_empty:
            print(" "*self.indent_all + "No results.")
            return
        self.format_first_line()
        self.format_details()
        if remove_color(self.first_line):
            print(" "*self.indent_all + self.first_line)
        if remove_color(self.first_line) and self.detail_groups:
            print(" "*self.indent_all + "\u2500"*self.approximate_string_length(self.first_line))
        for no, group in enumerate(self.detail_groups):
            for result in group:
                print(" "*(self.indent_all+self.indent_details) + result)
            if not no == len(self.detail_groups)-1:
                print(" "*self.indent_all + "\u2500"*self.approximate_string_length(self.first_line))
        print()

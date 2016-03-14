#!/usr/bin/python3
# -*- coding: utf8 -*-

from modules import colorama
from collection import Kanji

class ResultPrinter(object):
    def __init__(self, lst_of_lst, force_annotation=False):
        """
        :param lst_of_lst: List of (List of (KanjiObjects or Strings))
        :return:None
        """
        self.force_annotation = force_annotation
        self.result_groups = lst_of_lst

        if colorama:
            self.kanji_colors = [colorama.Fore.RED, colorama.Fore.BLUE]
            self.kana_colors = [colorama.Fore.CYAN]
            self.not_found_colors = [colorama.Fore.YELLOW]  # todo: not yet implemented
            self.default_color = colorama.Style.RESET_ALL
        else:
            # colorama not installed
            self.kanji_colors = [""]
            self.kana_colors = [""]
            self.not_found_colors = [""]
            self.default_color = ""

        self.first_line = self.default_color
        self.detail_groups = []  # list of lists

        self.indent_all = 4
        self.indent_details = 0

    def format_first_line(self):
        if len(self.result_groups) == 1 and len(self.result_groups[0]) >= 2:
            # first line unnescessary, leave it empty
            return
        for group_no, group in enumerate(self.result_groups):
            if not group:
                self.result_groups.remove(group)
                continue
            if len(group) >= 2:
                self.first_line += "("
            for result_no, result in enumerate(group):
                self.first_line += self.color_from_item(result, result_no, group_no)
                if isinstance(result, Kanji):
                    self.first_line += result.kanji
                elif isinstance(result, str):
                    self.first_line += result
                else:
                    raise ValueError
                self.first_line += self.default_color
            if len(group) >= 2:
                self.first_line += ")"

    def color_from_item(self, result, result_no, group_no):
        if isinstance(result, Kanji):
            return self.kanji_colors[group_no % len(self.kanji_colors)]
        elif isinstance(result, str):
            return self.kana_colors[group_no % len(self.kana_colors)]
        else:
            raise ValueError

    def format_details(self):
        if len(self.result_groups) == 1 and len(self.result_groups[0]) >= 2:
            self.format_details_single_group()
        elif len(self.result_groups) >= 2:
            self.format_details_multiple_groups()
        else:
            return

    def format_details_single_group(self):
        group = self.result_groups[0]
        details = []
        for result_no, result in enumerate(group):
            # alternating color in matches
            if isinstance(result, Kanji):
                details.append("{}{}: {}{}".format(self.kanji_colors[result_no % len(self.kanji_colors)],
                                                   result.kanji, result.meaning, self.default_color))
            elif isinstance(result, Kanji):
                details.append("{}{}{}".format(self.kana_colors[result_no % len(self.kana_colors)], result,
                                               self.default_color))
            else:
                raise ValueError
        self.detail_groups.append(details)

    def format_details_multiple_groups(self):
        for group_no, group in enumerate(self.result_groups):
            if len(group) >= 2:
                details = []
                for result_no, result in enumerate(group):
                    # same coloring as the groups
                    if isinstance(result, Kanji):
                        details.append("{}{}: {}{}".format(self.color_from_item(result, result_no, group_no),
                                                           result.kanji, result.meaning, self.default_color))
                    elif isinstance(result, Kanji):
                        details.append("{}{}{}".format(self.color_from_item(result, result_no, group_no), result,
                                                       self.default_color))
                    else:
                        raise ValueError
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
        if len(self.result_groups) == 0:
            print(" "*self.indent_all + "No results.")
            return
        self.format_first_line()
        self.format_details()
        print(" "*self.indent_all + self.first_line)
        if remove_color(self.first_line) and self.detail_groups:
            print(" "*self.indent_all + "\u2500"*self.approximate_string_length(self.first_line))
        for group in self.detail_groups:
            for result in group:
                print(" "*(self.indent_all+self.indent_details) + result)
        print()
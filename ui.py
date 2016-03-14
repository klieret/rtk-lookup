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

The user interface.
"""

import cmd
import sys
import os

global colorama
global logger

from modules import *
from util import *
from collection import *

# todo: force annotations

class ResultPrinter(object):
    def __init__(self, lst_of_lst, force_annotation=False):
        """
        :param lst_of_lst: List of (List of (KanjiObjects or Strings))
        :return:None
        """
        self.force_annotation = force_annotation
        self.result_groups = lst_of_lst

        self.kanji_colors = [colorama.Fore.RED, colorama.Fore.BLUE]
        self.kana_colors = [colorama.Fore.CYAN]
        self.not_found_colors = [colorama.Fore.YELLOW]  # todo: not yet implemented
        self.default_color = colorama.Style.RESET_ALL

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





class LookupCli(cmd.Cmd):
    """The command line interface (Cli). """

    def __init__(self, kc):
        cmd.Cmd.__init__(self)

        # KanjiCollection
        self.kc = kc

        # ----------- Configure me ----------------

        self.default_mode = 'default'
        self.commandSeparator = "."
        if " " in self.commandSeparator:
            raise ValueError("This would give problems later. No spaces in command separator.")

        # "Answers" get indented by this amount of spaces
        self.indent = 4

        # Color of the answers. Empty string: No color     
        self.answer_color = colorama.Fore.RED
        # todo: remove some of those (aren't used?)
        self.answer_color_2 = colorama.Fore.BLUE

        self.default_result_color = colorama.Fore.RED
        self.one_line_search_results_color = [colorama.Fore.RED, colorama.Fore.BLUE]
        self.search_results_color = [colorama.Fore.RED, colorama.Fore.BLUE]

        self.mode = self.default_mode
        self.update_prompt()

        # dict of modes of the form long_form (don't change): [abbrev/command, description]
        # todo: should be a class, not a dictionary
        self.modes = {'default': ['d', 'do nothing'],
                      'copy': ['c', 'Copy'],
                      'www': ['w', 'Lookup in the www.'],
                      'primitive': ['p', 'lookup kanji by primitives'],
                      'conditional': ['o', 'Lookup in the www if the search was guaranteed to be successful.'],
                      'story': ['s', 'Like default but also prints the story corresponding to the kanji.']}

        self.search_history = [] 

    def update_prompt(self):
        """Updates the prompt (self.promp) based on the mode.
        """
        self.prompt = "(%s) " % self.mode

    def default(self, line):
        """Default function that gets called on the input.
        :param line:
        :return:
        """
        if ';' in line:
            # multiple commands
            # call this function recursively
            lines = line.split(';')
            for line in lines:
                self.default(line)
            return

        line = line.strip().lower()

        if not line:
            self.emptyline()

        elif line.startswith(self.commandSeparator):
            command = line[1:].split(" ")[0]
            self.command(command)
            if " " in line:
                rest = ' '.join(line[1:].split(" ")[1:])
                self.default(rest)

        elif self.mode == "primitive":
            self.primitive(line)

        else:
            self.search_history.append(line)
            self.search(line)

    # todo: there should be a proper object, not just a string
    def print_results(self, result_groups, force_annotation=False):
        rp = ResultPrinter(result_groups, force_annotation=force_annotation)
        rp.print()

    # ----------- Handlers ---------------

    def emptyline(self):
        """Gets called if user presses <ENTER> without providing intput.
        :return: None
        """
        pass

    def change_mode(self, mode, silent=False):
        """Changes self.mode to mode (long form).
        :param mode
        :param silent
        :return
        """
        # ----------- switching not possible ---------------
        if mode in ['copy', 'www'] and not os.name == "posix":
            logger.warning("Mode %s currently only supported for linux." % mode)
            logger.debug("You can adapt the corresponding function in the source code!")
            return
        if mode == 'primitive' and not self.kc.stories_available:
            logger.warning("No user defined stories available. Mode unavailable.")
            return
        
        # ----------- switching possible -------------------
        if self.mode == mode:
            if not silent:
                logger.info("Mode %s is already active." % self.mode)
            return
        else:
            self.mode = mode
            if not silent:
                logger.info("Switched to mode %s." % self.mode)
            self.update_prompt()
            return

    def command(self, command):
        """Gets called if line starts with self.commandSeparator.
        :param command
        :return
        """
        if command == 'h':
            print("Basic commands: .q (quit), .h (help), .!<command> (run command in shell), .m (print current mode) ")
            print("Available modes:")
            for mode in self.modes:
                print("    %s (.%s): %s" % (mode, self.modes[mode][0], self.modes[mode][1]))
            return

        if command == 'q':
            logger.info("Bye.")
            sys.exit(0)

        if command == '':
            self.emptyline()
            return

        if command[0] == '!':
            os.system(command[1:])
            return

        if command == 'm':
            print("Current mode is %s." % self.mode)
            return

        for m in self.modes:
            if command == self.modes[m][0]:
                self.change_mode(m)
                return 
            elif command == self.commandSeparator + self.modes[m][0]:
                if not self.search_history:
                    logger.warning("Search history empty. Skipping that command. ")
                    return
                logger.info('Handling "%s" with mode %s.' % (self.search_history[-1], m))
                old_mode = self.mode
                self.change_mode(m, silent=True)
                self.default(self.search_history[-1])
                self.change_mode(old_mode, silent=True)
                return

        # if we come here, the command is not known.
        logger.warning("Command not known. Type '.h' for help.")
        return

    def primitive(self, line):
        """Looks for kanjis based on primitives.
        :param line
        :return
        """
        # Kanjis that match the description
        candidates = self.kc.primitive_search(line.split(' '))
        self.print_results([candidates], force_annotation=True)

    # todo: shouldn't do any printing; only assemble an appropriate return object
    def search(self, line):
        """Looks for kanjis based on RTK indizes or meanings.
        :param line
        :return
        """
        # are we sure that the search was successful
        # and returned exactly 1 result?
        guaranteed_hit = True

        # split up segments
        segments = line.split(' ')

        # save current mode to temporarily change mode
        # if the current mode doesn't make sense in the context
        # (e.g. lookup mode if more than one expression was found)
        tmp_mode = self.mode

        result_groups = []
        force_annotation = False

        for segment in segments:

            matching_kanjis = self.kc.search(segment)


            if len(matching_kanjis) == 0:
                # no kanji matches the description. Konvert to hiragana.
                
                guaranteed_hit = False
                if romkan:
                    result_groups.append([romkan.to_hiragana(segment)])
                else:
                    result_groups.append([segment])

            elif len(matching_kanjis) == 1:
                # there is exactly 1 kanji matching the search pattern
                
                result_groups.append(matching_kanjis)

                if any(letter in line for letter in ['?', '+', '%']):
                    force_annotation = True

            else:
                self.mode = "nothing"
                result_groups.append(matching_kanjis)

            # todo: story mode
            # if self.mode == 'story':
            #     for h in matching_kanjis:
            #         annotations += "%s: %s\n" % (h.kanji, h.story)

        # ans = ans.strip()
        # annotations = annotations.strip()
        # if annotations:
        #     ans += "\n\n-----------------\n"
        #     ans += annotations
        #
        # todo: copying etc.
        # if self.mode == 'copy':
        #     copy_to_clipboard(remove_color(ans))
        # elif self.mode == 'www':
        #     lookup(remove_color(ans))
        # elif self.mode == "conditional":
        #     if guaranteed_hit:
        #         logger.info("Guaranteed hit. Looking up.")
        #         lookup(remove_color(ans))
        #     else:
        #         logger.info("No guaranteed hit. Doing nothing.")
        # elif self.mode == "nothing":
        #     pass

        # reset mode
        self.mode = tmp_mode

        self.print_results(result_groups, force_annotation)

#!/usr/bin/python3
# -*- coding: utf8 -*-

""" The user interface.
"""

import cmd
import os
import sys
from rtklookup.util import lookup, copy_to_clipboard
from rtklookup.log import logger
from rtklookup.collection import KanjiCollection
from rtklookup.searchresults import SearchResultGroup, SearchResult
from rtklookup.resultprinter import ResultPrinter


class LookupCli(cmd.Cmd):
    """The command line interface (Cli). """
    def __init__(self, kanji_collection: KanjiCollection):
        cmd.Cmd.__init__(self)

        # KanjiCollection
        self.kanji_collection = kanji_collection

        # todo: move to config?
        self.default_mode = 'default'
        self.cmd_separator = "."

        if " " in self.cmd_separator:
            raise ValueError("This would give problems later. "
                             "No spaces in command separator.")

        self.mode = self.default_mode
        self.update_prompt()

        # dict of modes of the form
        # long_form (don't change): [abbrev/command, description]
        self.modes = {'default': ['d', 'do nothing'],
                      'copy': ['c', 'Copy'],
                      'www': ['w', 'Lookup in the www.'],
                      'primitive': ['p', 'lookup kanji by primitives'],
                      'conditional': ['o', 'Lookup in the www if the search '
                                           'was guaranteed to be successful.'],
                      'story': ['s', 'Like default but also prints the story '
                                     'corresponding to the kanji.']}

        self.search_history = []

    def update_prompt(self):
        """Updates the prompt (self.promp) based on the mode.
        """
        self.prompt = "(%s) " % self.mode

    def default(self, line: str):
        """Default function that gets called on the input.
        :param line:
        :return:
        """
        if ';' in line:
            # multiple commands
            # call this function recursively!
            lines = line.split(';')
            for line in lines:
                self.default(line)
            return

        line = line.strip().lower()

        if not line:
            self.emptyline()
        elif line.startswith(self.cmd_separator):
            command = line[1:].split(" ")[0]
            rest = ""
            if " " in line:
                rest = ' '.join(line[1:].split(" ")[1:])
            self.command(command, rest=rest)
        elif self.mode == "primitive":
            self.search_primitive(line)
        else:
            self.search_history.append(line)
            self.search_general(line)

    @staticmethod
    def print_results(search_item_collection: SearchResult):
        # print(search_item_collection)
        rp = ResultPrinter(search_item_collection)
        rp.print()

    # ----------- Handlers ---------------

    def emptyline(self):
        """Gets called if user presses <ENTER> without providing input.
        :return: None
        """
        pass

    def change_mode(self, mode: str, silent=False):
        """Changes self.mode to mode (long form).
        :param mode
        :param silent
        :return
        """
        if mode in ['copy', 'www'] and not os.name == "posix":
            logger.warning("Mode %s currently only supported for linux." %
                           mode)
            logger.debug("You can adapt the corresponding function in the "
                         "source code!")
        elif mode == 'primitive' and not \
                self.kanji_collection.stories_available:
            logger.warning("No user defined stories available. "
                           "Mode unavailable.")
        elif self.mode == mode:
            if not silent:
                logger.info("Mode %s is already active." % self.mode)
        else:
            self.mode = mode
            if not silent:
                logger.info("Switched to mode %s." % self.mode)
            self.update_prompt()

    def command(self, command: str, rest=""):
        """Gets called if line starts with self.commandSeparator.
        :param command
        :param rest of the user input after space.
        :return
        """
        if command == 'h':
            print("Basic commands: .q (quit), .h (help), .!<command> "
                  "(run command in shell), .m (print current mode) ")
            print("Available modes:")
            for mode in self.modes:
                print("    %s (.%s): %s" % (mode, self.modes[mode][0],
                                            self.modes[mode][1]))
            return
        elif command == 'q':
            logger.info("Bye.")
            sys.exit(0)
        elif command == '':
            self.emptyline()
            return
        elif command[0] == '!':
            os.system(command[1:])
            return
        elif command == 'm':
            print("Current mode is %s." % self.mode)
            return

        # changing modes
        for mode in self.modes:
            if command == self.modes[mode][0]:
                if not rest:
                    self.change_mode(mode)
                else:
                    # temporarily change mode, lookup rest, then change back
                    old_mode = self.mode
                    self.change_mode(mode)
                    self.default(rest)
                    self.change_mode(old_mode)
                return
            elif command == self.cmd_separator + self.modes[mode][0]:
                # corresponding to user input of 2 cmd_separators
                if not self.search_history:
                    logger.warning("Search history empty. "
                                   "Skipping that command. ")
                    return
                logger.info('Handling "%s" with mode %s.' %
                            (self.search_history[-1], mode))
                old_mode = self.mode
                self.change_mode(mode, silent=True)
                self.default(self.search_history[-1])
                self.change_mode(old_mode, silent=True)
                return

        # if we come here, the command is not known.
        logger.warning("Command not known. Type '.h' for help.")

    def search_primitive(self, line: str):
        """Looks for kanjis based on primitives.
        :param line
        :return
        """
        # Kanjis that match the description
        search_item_collection = SearchResult(line, mode=self.mode)
        search_item_collection.groups = [SearchResultGroup(line)]
        search_item_collection.groups[0].kanji = \
            self.kanji_collection.primitive_search(line.split(' '))
        if not search_item_collection.groups[0].has_kanji:
            # no results
            search_item_collection.groups = []
        self.print_results(search_item_collection)

    def search_general(self, line: str):
        """Looks for kanjis based on RTK indices or keywords.
        :param line
        :return
        """
        # are we sure that the search was successful
        # and returned exactly 1 result? > for conditional mode

        # split up in search words (i.e. single search entries)
        search_words = line.split(' ')
        result = SearchResult(line, mode=self.mode)
        result.groups = \
            [SearchResultGroup(search_word) for search_word in search_words]

        # perform the searches
        for search_item in result:
            search_item.kanji = \
                self.kanji_collection.search(search_item.search)

        if self.mode == 'story':
            # todo: Implement Story mode
            raise NotImplementedError
        if self.mode == 'copy':
            copy_to_clipboard(result.copyable_result())
        elif self.mode == 'www':
            lookup(result.copyable_result())
        elif self.mode == "conditional":
            if result.unique_success:
                logger.info("Guaranteed hit. Looking up.")
                lookup(result.copyable_result())
            else:
                logger.info("No guaranteed hit. Doing nothing.")
        elif self.mode == "nothing":
            pass

        self.print_results(result)

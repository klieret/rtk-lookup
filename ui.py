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

global logger

from modules import *
from util import *
from collection import *
from searchresults import SearchItem, SearchItemCollection

# todo: force annotations


from resultprinter import ResultPrinter

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
            # call this function recursively!
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

    @staticmethod
    def print_results(search_item_collection):
        # print(search_item_collection)
        rp = ResultPrinter(search_item_collection)
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
        if mode in ['copy', 'www'] and not os.name == "posix":
            logger.warning("Mode %s currently only supported for linux." % mode)
            logger.debug("You can adapt the corresponding function in the source code!")
        elif mode == 'primitive' and not self.kc.stories_available:
            logger.warning("No user defined stories available. Mode unavailable.")
        elif self.mode == mode:
            if not silent:
                logger.info("Mode %s is already active." % self.mode)
        else:
            self.mode = mode
            if not silent:
                logger.info("Switched to mode %s." % self.mode)
            self.update_prompt()

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

    def primitive(self, line: str):
        """Looks for kanjis based on primitives.
        :param line
        :return
        """
        # Kanjis that match the description
        search_item_collection = SearchItemCollection(line)
        search_item_collection.items = [SearchItem(line)]
        search_item_collection.items[0].kanji = self.kc.primitive_search(line.split(' '))
        self.print_results(search_item_collection)

    # todo: shouldn't do any printing; only assemble an appropriate return object
    def search(self, line: str):
        """Looks for kanjis based on RTK indizes or meanings.
        :param line
        :return
        """
        # are we sure that the search was successful
        # and returned exactly 1 result? > for conditional mode

        # split up in search words (i.e. single search entries)
        search_words = line.split(' ')
        search_item_collection = SearchItemCollection(line)
        search_item_collection.items = [SearchItem(search_word) for search_word in search_words]

        # perform the searches
        for search_item in search_item_collection:
            # todo: does this update or copy?
            search_item.kanji = self.kc.search(search_item.search)

            # todo: story mode
            # if self.mode == 'story':
            #     for h in matching_kanjis:
            #         annotations += "%s: %s\n" % (h.kanji, h.story)

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
        #
        self.print_results(search_item_collection)
        # self.print_results(result_groups, force_annotations)

#!/usr/bin/python3
# -*- coding: utf8 -*-

"""
Lookup Kanji by Heisig Keyword or frame number
----------------------------------------------

See https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword.git
for more information.

**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU GPL, version 3 or later
"""

import cmd
import sys
import os

global colorama
global logger

from modules import *
from util import *

class LookupCli(cmd.Cmd):
    """ The command line interface (Cli). """

    def __init__(self, kc):
        super().__init__()

        # KanjiCollection
        self.kc = kc

        # ----------- Configure me ----------------

        self.defaultMode = 'default'
        self.commandSeparator = "."

        # "Answers" get indented by this amount of spaces
        self.indent = 4

        # Color of the answers. Empty string: No color     
        self.answerColor = colorama.Fore.RED
        self.answerColor2 = colorama.Fore.BLUE     

        # -----------------------------------------

        self.mode = self.defaultMode
        self.update_prompt()

        # dict of modes of the form long_form (don't change): [abbrev/command, description]
        self.modes = { 'default': ['d', 'do nothing'], 
                       'copy': ['c', 'Copy'], 
                       'www': ['w', 'Lookup'],
                       'primitive': ['p', 'lookup kanji by primitives']}

        self.search_history = [] 

    def update_prompt(self):
        """ Updates the prompt (self.promp) based on the mode. """

        self.prompt = "[%s] " % self.mode

    def default(self, line):
        """ Default function that gets called on the input. """
        
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
            command = line[1:]
            self.command(command)

        elif self.mode == "primitive":
            ans = self.primitive(line)
            if ans:
                self.ansPrinter(ans)
            else:
                self.ansPrinter("No result. ")

        else:
            self.search_history.append(line)
            ans = self.search(line)
            if ans:
                self.ansPrinter(ans)
            else:
                self.ansPrinter("No result. ")


    def ansPrinter(self, ans):
        """ Prints the Kanji results. A simple print(ans) would do, 
        but wrapping it into a function allows for e.g. coloring or
        indenting. """

        print(self.answerColor)
        
        lines = ans.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            print(" "*4 + line) 
        
        print(colorama.Style.RESET_ALL)

    # ----------- Handlers ---------------

    def emptyline(self):
        """ Gets called if user presses <ENTER> without providing intput. """
        pass

    def change_mode(self, mode, silent=False):
        """ Changes self.mode to mode (long form). """
        # ----------- switching not possible ---------------
        if mode in ['copy', 'www'] and not os.name == "posix":
            logger.warning("Mode %s currently only supported for linux." % mode)
            logger.debug("You can adapt the corresponding function in the source code!")
            return
        if mode == 'primitive' and not self.kc.storiesAvailable:
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
        """ Gets called if line starts with self.commandSeparator. """

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
                old_mode = self.mode
                self.change_mode(m, silent=True)
                self.default(self.search_history[-1])
                self.change_mode(old_mode, silent=True)
                return

        # if we come here, the command is not known.
        logger.warning("Command not known. Type '.h' for help.")
        return

    def primitive(self, line):
        """ Looks for kanjis based on primitives. """
        
        # Kanjis that match the description
        candidates = self.kc.story_search(line.split(' '))
        
        # Return line
        ans = ""

        for candidate in candidates:
            kanjiObj = self.kc.kanjiObjFromPos(candidate)
            ans += "%s: %s\n" % (kanjiObj.kanji, kanjiObj.meaning)
        
        return ans

    def search(self, line):
        """ Looks for kanjis based on RTK indizes or meanings. """

         # split up segments
        segs = line.split(' ')

        # save current mode to temporarily change mode
        # if the current mode doesn't make sense in the context
        # (e.g. lookup mode if more than one expression was found)
        tmp_mode = self.mode

        # Return line
        ans = ""
        annotations = ""    # will be appended to ans at the end
        segNo = -1
        color = [self.answerColor, self.answerColor2]
        for seg in segs:
            segNo += 1
            
            # alternating colors
            ans += color[segNo % len(color)]

            hits = self.kc.search(seg)

            if len(hits) == 0:
                # no kanji matches the description. Konvert to hiragana.
                if romkan:
                    ans += romkan.to_hiragana(seg)
                else:
                    ans += seg

            elif len(hits) == 1:
                # there is exactly 1 kanji matching the search pattern
                ans += self.kc.kanjiObjFromPos(hits[0]).kanji

            else:
                # there ist more than 1 kanji matching the search pattern
                self.mode = "nothing"

                if len(segs) == 1:
                    # only one search pattern is given
                    for h in hits:
                        ans += "%s: %s\n" % (self.kc.kanjiObjFromPos(h).kanji, self.kc.kanjiObjFromPos(h).meaning)
                else:
                    # multiple search pattern are given
                    # group the matching kanji for a result that fits in one line
                    ans += '('
                    for h in hits:
                        ans += "%s" % (self.kc.kanjiObjFromPos(h).kanji)
                    # strip last ', '
                    ans = ans[:-1]
                    ans += ')'
                    # give the keywords for the multiple search results
                    # as an annotation below the answer line
                    annotations += self.search(seg)

            ans += colorama.Style.RESET_ALL

        ans = ans.strip()
        annotations = annotations.strip()
        if annotations:
            ans += "\n\n-----------------\n"
            ans += annotations

        if self.mode == 'copy':
            copy_to_clipboard(removeColor(ans))
        elif self.mode == 'www':
            lookup(removeColor(ans))
        elif self.mode == "nothing":
            pass

        # reset mode
        self.mode = tmp_mode
       
        return ans
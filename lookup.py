#!/usr/bin/python3
# -*- coding: utf8 -*-

"""
Lookup Kanji by Heisig Keyword or frame number

See https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword.git
or http://ch4noyu.bitbucket.org/ for more information.

**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU AGPL, version 3 or later

The list of all kanji by heisig number "RTK.tsv" was included in an Anki plugin
with:

**Copyright**: Ian Worthington <Worthy.vii@gmail.com>

**License:** GNU GPL, version 3 or later

"""

# todo: run with console arguments
# todo: which heisig version are we using?

# to enable up and down arrows etc.

import os
import logging
import csv
import sys

logging.basicConfig(level=logging.DEBUG)

# 'romkan' is the module used to convert
# hiragana to romanji. It is available at https://pypi.python.org/pypi/romkan
try:
    import romkan
except ImportError:
    romkan = None
    logging.warning("Romkan module not found. No Support for hiragana.")
    logging.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")

# ---------- CUSTOMIZE ME --------


def copy_to_clipboard(clip):
    """ Copies argument to clipboard. """
    # Check if we are running on linux:
    success = 1
    if os.name == "posix":
        success = os.system("echo '%s' | xclip -selection c" % clip)
    return success


def lookup(clip):
    """ Looks up phrase in the www """
    # Check if we are running on linux:
    success = 1
    if os.name == "posix":
        success = os.system("firefox http://tangorin.com/general/dict.php?dict=general\&s=%s &" % clip)
    return success

# ----------------------------------


# dict of modes of the form long_form (don't change): [abbrev (free to adapt!), description]
modes = {'nothing': ['n', 'do nothing'], 'copy': ['c', 'Copy'], 'www': ['w', 'Lookup']}

# ----------------------------------

# stores all information
kanjis = []

# ------------ load kanji database ---------
with open("RTK.tsv", 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        kanjis.append(row)


# ------------ the actual search ------------
def search(word):
    """
    Does the actual search.
    :param: search
    :return: A list of tuples of the form ("<kanji>", "<keyword>") (or ("<string>", "?") if no kanji is found.)
    """

    word = word.replace('_', ' ')
    found = []

    if word.isdigit():
        for kanji in kanjis:
            if str(kanji[1]) == word:
                found.append((kanji[0], kanji[3]))
    else:
        if word[-1] == "?":
            for kanji in kanjis:
                if word[:-1] in str(kanji[3]):
                    found.append((kanji[0], kanji[3]))
        elif word[-1] == "+":
            for kanji in kanjis:
                if word[:-1] in str(kanji[3]).split(' '):
                    found.append((kanji[0], kanji[3]))
        else:
            for kanji in kanjis:
                if word == str(kanji[3]):
                    found.append((kanji[0], kanji[3]))

    # if not found: simply convert to hiragana
    if not found:
        if romkan:
            found.append((romkan.to_hiragana(word), '?'))
        else:
            found.append((word, '?'))

    return found

import cmd


class LookupCli(cmd.Cmd):

    def __init__(self):
        super().__init__()

        # ----------- Configure me ----------------

        self.defaultMode = 'nothing'
        self.prompt = "Inpt: "
        self.commandSeparator = "."

        # -----------------------------------------

        self.mode = self.defaultMode

    def emptyline(self):
        pass

    def default(self, line):
        line = line.strip()

        # Commands

        if line == self.commandSeparator + 'q':
            logging.info("Bye.")
            sys.exit(0)

        if line == self.commandSeparator + '':
            self.emptyline()
            return

        for m in modes:
            if line == self.commandSeparator + modes[m][0]:
                if m in ['copy', 'www'] and not os.name == "posix":
                    logging.warning("Modes currently only supported for linux.")
                    return
                self.mode = m
                logging.info("Switched to mode %s." % self.mode)
                return

        # split up segments
        segs = line.split(' ')

        # save current mode to temporarily change mode
        tmp_mode = self.mode

        # Return line
        ans = ""

        for seg in segs:
            hits = search(seg)

            if len(hits) == 1:
                ans += hits[0][0]
            if len(hits) > 1:
                self.mode = "nothing"
                ans += str(hits)

        print(ans)
        print()

        if self.mode == 'copy':
            copy_to_clipboard(ans)
        elif self.mode == 'www':
            lookup(ans)
        elif self.mode == "nothing":
            pass

        # reset mode
        self.mode = tmp_mode

if __name__ == '__main__':
    LookupCli().cmdloop()

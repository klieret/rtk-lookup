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

# todo: logging
# todo: update screenshot
# todo: move active parts
# todo: surpess logging when running with cl arguments
# todo: help
# todo: documentation of primitive mode
# todo: more flexibility in handling csv files > transform into object
# todo: which heisig version are we using?
# additional newline?

# to enable up and down arrows etc.

import os
import os.path
import logging
import csv
import sys
import cmd

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
modes = {'nothing': ['n', 'do nothing'], 'copy': ['c', 'Copy'], 'www': ['w', 'Lookup'],
         'primitive': ['p', 'lookup kanji by primitives']}

# ------------ load kanji database ---------

kanjis = []
rtkFile = "RTK.tsv"
if os.path.exists(rtkFile):
    with open(rtkFile, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            kanjis.append(row)
else:
    logging.critical("File %s (contains heisig indizes) not found. Exiting." % rtkFile)

# ------------- load stories db ----------------

stories = []
storiesFile = "kanji_stories.tsv"
if os.path.exists(storiesFile):
    with open(storiesFile, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            stories.append(row)
else:
    logging.warning("File %s (contains user stories) not found. Primitive mode unavailable.")


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


def story_search(primitives):
    results = []
    for kanji in stories:
        found = True
        for p in primitives:
            if not p.replace("_", " ") in kanji[3]:
                found = False
        if found:
            results.append(kanji)
    return results


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

        if line.startswith('.'):
            command = line[1:]

            if command == 'h':
                print("Basic commands: .q (quit), .h (help), .!<command> (run command in shell), .m (print current mode) ")
                print("Available modes: %s" % str(modes))
                print()
                return

            if command == 'q':
                logging.info("Bye.")
                sys.exit(0)

            if command == '':
                self.emptyline()
                return

            if command[0] == '!':
                os.system(command[1:])
                return

            if command == 'm':
                logging.info("Current mode is %s." % self.mode)
                return

            for m in modes:
                if command == modes[m][0]:
                    # ----------- switching not possible ---------------
                    if m in ['copy', 'www'] and not os.name == "posix":
                        logging.warning("Mode %s currently only supported for linux." % m)
                        return
                    if m == 'primitive' and not stories:
                        logging.warning("No user defined stories available. Mode unavailable.")
                        return
                    # ----------- switching possible -------------------
                    if self.mode == m:
                        logging.info("Mode %s is already active." % self.mode)
                        return
                    else:
                        self.mode = m
                        logging.info("Switched to mode %s." % self.mode)
                        return

            # if we come here, the command is not known.
            logging.warning("Command not known. Type '.h' for help. \n")
            return

        # Input

        if self.mode == "primitive":
            candidates = story_search(line.split(' '))
            for c in candidates:
                print("%s: %s" % (c[0], c[1]))
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
            else:
                self.mode = "nothing"

                if len(segs) == 1:
                    for h in hits:
                        ans += "%s: %s\n" % (h[0], h[1])
                else:
                    ans += str(hits)

        ans = ans.rstrip()
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
    if len(sys.argv) == 1:
        LookupCli().cmdloop()
    else:
        lines = ' '.join(sys.argv[1:]).split(",")
        cli = LookupCli()
        for l in lines:
            l = l.lstrip()    # else it matters whether there is a space in front of the ','
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)
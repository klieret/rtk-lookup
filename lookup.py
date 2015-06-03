#!/usr/bin/python3
 # -*- coding: utf-8 -*-

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

# todo: use the python module for elegant console interfaces
# todo: rewrite with class
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
romkanSupport = True
try:
    import romkan
except ImportError:
    logging.warning("Romkan module not found. No Support for hiragana.")
    logging.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")
    romkanSupport = False

# ---------- CUSTOMIZE ME --------

commandSeparator = "."
defaultMode = 'n'
prompt = "Inpt: "


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


# dict of modes of the form longform (don't change): abbrev (free to adapt!), description
modes = {'nothing': ['n', 'do nothing'], 'copy': ['c', 'Copy'], 'www': ['w', 'Lookup']}

# ----------------------------------

# stores all information
kanjis = []
# stores mode
mode = defaultMode

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
        if romkanSupport:
            found.append((romkan.to_hiragana(word), '?'))
        else:
            found.append((word, '?'))

    return found

# ------------ main loop ------------


while True:
    string = input(prompt).strip()

    if string == "":
        continue

    # Commands

    skip = False

    if string == commandSeparator + 'q':
        logging.info("Bye.")
        sys.exit(0)
    if string == commandSeparator + '':
        skip = True

    for m in modes:
        if string == commandSeparator + modes[m][0]:
            mode = m
            logging.info("Switched to mode %s." % mode)
            skip = True

    if skip:
        print()
        continue

    # split up segments
    segs = string.split(' ')
    ans = ""



    # save current mode to temporarily change mode
    tmpMode = mode

    ans = ""

    for seg in segs:
        hits = search(seg)

        if len(hits) == 1:
            ans += hits[0][0]
        if len(hits) > 1:
            mode = "nothing"
            ans += str(hits)

    print(ans)
    print()

    if mode == 'copy':
        copy_to_clipboard(ans)
    elif mode == 'www':
        lookup(ans)
    elif mode == "nothing":
        pass

    # reset mode
    mode = tmpMode
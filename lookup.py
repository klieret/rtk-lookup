#!/usr/bin/python3
"""
Input: combination of some of the following
            - Heisig's keyword of a kanji (if the keyword contains a space " ",
                write "_" instead)
            - "word+" will look for all keywords of the form "word1 word2 word3" where word matches one of the word1,...
            - if you're not sure whether the keyword is "go" or "going", write "go?" it will look for all words that contain "go"
            - Heisig's number of a kanji
            - other romanji (will be converted to hiragana if not found)
            - -q (quit), :<mode> (switch to another mode)
    Output: Kanji+hiragana.
    Modes:
            - x (nothing): do nothing
            - n (normal): just copy to clipboard
            - t (tangorin): look up in the www (default is firefox and tangorin)
    Change via .<mode-name>.
"""

# todo: Use the python module for console interfaces
# todo: change to relative path of csv
# to enable up and down arrows etc.

import os
import logging
import csv

# 'romkan' is the module used to convert
# hiragana to romanji. It is available at https://pypi.python.org/pypi/romkan
romkanSupport = False
try:
    import romkan
except ImportError:
    logging.warning("Romkan module not found. No Support for hiragana.")
    logging.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")
    romkanSupport = True

# ---------- CUSTOMIZE ME --------

commandSeparator = "."
defaultMode = 'n'
prompt = "Phrase: "


def copy_to_clipboard(clip):
    """ Copies argument to clipboard. """
    # Check if we are running on linux:
    if os.name == "posix":
        success = os.system("echo '%s' | xclip -selection c" % clip)
    return success


def lookup(clip):
    """ Looks up phrase in the www """
    # Check if we are running on linux:
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

# ------------ load information ---------
with open("/home/fuchur/Documents/japan/programs/rtk_lookup/RTK.tsv", 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        kanjis.append(row)


# ------------ main loop ------------
while True:
    string = input(prompt)

    if string == "":
        continue

    # Commands

    if string == commandSeparator + 'q':
        break
    if string == commandSeparator + '':
        continue

    for m in modes:
        if string == commandSeparator + modes[m][0]:
            mode = m
            logging.info("Switchted to mode %s." % mode)

    # split up segments
    segs = string.split(' ')
    ans = ""

    for seg in segs:
        found = []
        if seg.isdigit():
            for kanji in kanjis:
                if str(kanji[1]) == seg:
                    found.append((kanji[0], kanji[3]))
        else:
            if seg[-1] == "?":
                for kanji in kanjis:
                    if seg[:-1] in str(kanji[3]):
                        found.append((kanji[0], kanji[3]))
            elif seg[-1] == "+":
                for kanji in kanjis:
                    if seg[:-1] in str(kanji[3]).split(' '):
                        found.append((kanji[0], kanji[3]))
            else:
                for kanji in kanjis:
                    if seg.replace('_', ' ') == str(kanji[3]):
                        found.append((kanji[0], kanji[3]))

        # if not found: simply convert to hiragana
        if not found and romkanSupport:
            found.append((romkan.to_hiragana(seg), '?'))

        # save current mode to temporarily change mode
        tmpMode = mode

        if len(found) == 1:
            ans += found[0][0]
        if len(found) > 1:
            mode = "x"
            ans += str(found)

    print(ans)

    if mode == 'copy':
        copy_to_clipboard(ans)
    elif mode == 'www':
        lookup(ans)
    elif mode == "nothing":
        pass

    # reset mode
    mode = tmpMode
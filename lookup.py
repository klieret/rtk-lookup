#!/usr/bin/python3
"""
# Lookup Kanji by Heisig Keyword or frame number

## Short Description
A little command line interface that allows to look up kanji with the
respective heisig keyword or frame number.

![lookup.png](https://bitbucket.org/repo/qe4bg9/images/274375207-lookup.png)

Examples:

    inpt: large resist
    大抵

    inpt: 107 1832
    大抵

    inpt: large 1832
    大抵

If words are not found, they are converted to hiragana. This requires the
```romkan``` module which can be downloaded
[here](https://pypi.python.org/pypi/romkan).

Examples:

    inpt: large てい
    大てい

    inpt: large 抵
    大抵

    inpt: large tei
    大てい

To quit, type ```.q```.

## Modes

There are three modes (in parenthesis: command to activate mode)

* copy (```.c```): Copy result to clipboard.
* lookup (```.w```): Lookup expression (default: tangorin.com with firefox)
* nothing (```.n```): Do nothing.

If more than one match is found, no action will be performed, regardless of the
current mode.
The default mode is ```c``` (but this can easily be changed in the source, as
well as the commands above).

## More on searching

If a keyword contains a space, substitute ```_```:

    inpt: sign_of_the_hog
    亥

```word+``` will look for all keywords of the form "word1 word2 word3" where
word matches (exactly) one of the words. If
there are multiple matches, all of them are printed as a list.

    Inpt: sign+
    [('酉', 'sign of the bird'), ('亥', 'sign of the hog'), ('寅', 'sign of
the tiger'), ('辰', 'sign of the dragon'), ('丑', 'sign of the cow'), ('卯',
'sign of the hare'), ('巳', 'sign of the snake')]

    Inpt: fish+
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]

    Inpt: fish
    魚

    Inpt: fin+
    鰭

    Inpt: fish+ thunder
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]雷

```word?``` will look for all keywords that contain "word":

    Inpt: Inpt: goi?
    行

    Inpt: fish?
    [('貝', 'shellfish'), ('乙', 'fish guts'), ('魚', 'fish'), ('漁',
'fishing'), ('恣', 'selfish'), ('鰭', 'fish fin')]

    Inpt: fish+
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]

## Installation:

Download the file ```lookup.py```. And run it with ```python3 lookup.py```.

## Issues, Suggestions, Feature Requests etc.
Open a ticket at [this addon's gitbucket issue
page](https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword/issues?status
=new&status=open) (prefered method, also works anonymously without login) or
send me an [e-mail](mailto:ch4noyu@yahoo.com). German is fine, too. I am not a
professional programmer, so feedback on how to improve my code is welcome, too.

## Source
The source is hostet at [this addon's bitbucket
page](https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword/overview).

## Copyright
**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU AGPL, version 3 or later

The list of all kanji by heisig number "RTK.tsv" was included in an Anki plugin
with:

**Copyright**: Ian Worthington <Worthy.vii@gmail.com>

**License:** GNU GPL, version 3 or later

## History

* 31 Mai 2015: First version released.
"""

# todo: use the python module for elegant console interfaces
# todo: rewrite with class
# todo: run with console arguments
# todo: which heisig version are we using?

# to enable up and down arrows etc.

import os
import logging
import csv

# 'romkan' is the module used to convert
# hiragana to romanji. It is available at https://pypi.python.org/pypi/romkan
romkanSupport = True
try:
    import romkan
except ImportError:
    logging.warning("Romkan module not found. No Support for hiragana.")
    logging.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")
    romkanSupport = False

logging.basicConfig(level=logging.DEBUG)

# ---------- CUSTOMIZE ME --------

commandSeparator = "."
defaultMode = 'n'
prompt = "Inpt: "


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

# ------------ load kanji database ---------
with open("RTK.tsv", 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
        kanjis.append(row)


# ------------ the actual search ------------
def lookup(search):
    """
    Does the actual search.
    :param: search
    :return: A list of tuples of the form ("<kanji>", "<keyword>") (or ("<string>", "?") if no kanji is found.)
    """
    # split up segments
    segs = search.split(' ')
    ans = ""

    for seg in segs:
        found = []
        seg = seg.replace('_', ' ')

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
                    if seg == str(kanji[3]):
                        found.append((kanji[0], kanji[3]))

        # if not found: simply convert to hiragana
        if not found:
            if romkanSupport:
                found.append((romkan.to_hiragana(seg), '?'))
            else:
                found.append((seg, '?'))

    return found

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
            logging.info("Switched to mode %s." % mode)

    found = lookup(string)

    # save current mode to temporarily change mode
    tmpMode = mode

    ans = ""
    
    if len(found) == 1:
        ans += found[0][0]
    if len(found) > 1:
        mode = "x"
        ans += str(found)

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
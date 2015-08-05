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
# todo: which heisig version are we using?

# to enable up and down arrows etc.

import os
import os.path
import logging
import csv
import sys
import cmd

logging.basicConfig(level=logging.DEBUG)

# The 'romkan' module is used to convert hiragana to romanji (optional).
# It is available at https://pypi.python.org/pypi/romkan
try:
    import romkan
except ImportError:
    romkan = None
    logging.warning("Romkan module not found. No Support for hiragana.")
    logging.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")

# The 'colorama' module is  used to display colors in a platform independent way (optional). 
# It is available at https://pypi.python.org/pypi/colorama
try:
    import colorama
except ImportError:
    colorama = None
    logging.warning("Colorama module not found. No Support for colors.")
    logging.debug("Colorama is available at https://pypi.python.org/pypi/colorama.")
else:
    colorama.init()


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



class Kanji(object):
    """ An object of this Class contains a kanji with the corresponding 
    information (index, meaning, story etc.) """
    
    def __init__(self, kanji):
        self.kanji = kanji            
        self.index = None
        self.meaning = None
        self.story = None

class KanjiCollection(object):
    """ An object of this Class bundles many Kanji objects. """
    
    def __init__(self):
        self.kanjis = []

        # did we load any stories?
        self.storiesAvailable = False 

    # ------------- Load information from files -------------------------------

    def updateRTK(self):
        """ Load the file that contains the RTK kanji, indizes and meanings. """

        # --------- CONFIGURE ME ---------

        rtkFile = "RTK.tsv"
        delimeter = '\t'
        kanjiColumn = 0
        indexColumn = 1
        meaningColumn = 3

        # --------------------------------
        
        if not os.path.exists(rtkFile):
            logging.fatal("File %s (to contain heisig indizes) not found. Exiting." % rtkFile)
            sys.exit(1)
        
        with open(rtkFile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanjiColumn].strip()
                index = row[indexColumn].strip()
                meaning = row[meaningColumn].strip()
                
                kanjiObj = Kanji(kanji)
                kanjiObj.index = index
                kanjiObj.meaning = meaning

                self.kanjis.append(kanjiObj)

    def updateStories(self):
        """ Load file that contains the RTK kanji, indizes and meanings. """

        # --------- CONFIGURE ME ---------

        storyFile = "kanji_stories.tsv"
        delimeter = '\t'
        kanjiColumn = 0
        storyColumn = 3

        # --------------------------------
        
        if not os.path.exists(storyFile):
            logging.warning("File %s (contains user stories) not found. Primitive mode will be unavailable.")
            self.storiesAvailable = False
        else:
            self.storiesAvailable = True
        
        with open(storyFile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanjiColumn].strip()
                story = row[storyColumn].strip()

                pos = self.posFromKanji(kanji) 
                if pos:
                    self.kanjis[pos].story = story
                else:
                    logging.warning("Could not update story for %s." % kanji)

    # ------------- pos <> .... -------------------------------
    # Most functions (e.g. search, etc.) will return the position
    # of the KanjiObj corresponding to the matched kanjis in self.kanjis.


    def kanjiObjFromPos(self, pos):
        """ Returns the kanji belonging to the KanjiObj at position pos 
        in self.kanjis. """
        
        return self.kanjis[pos]

    def posFromKanji(self, kanji):
        """ Given a kanji, returns the position of the corresponding
        Object of class 'Kanji' in self.kanjis. """

        i = 0
        for kanjiObj in self.kanjis:
            if kanjiObj.kanji == kanji:
                return i
            i+=1

        # if not found:
        return None

    # ------------- Search -------------------------------

    def search(self, word):
        """
        Does the actual search.
        :param word: search phrase
        :return: The positions of the matching kanjiObjs in self.kanjis (as a list)
        """

        word = word.replace('_', ' ')
        found = []

        i = 0
        for kanjiObj in self.kanjis:
            if word.isdigit():
                # searching for RTK index
                if kanjiObj.index == word:
                    found.append(i)
            else:
                if word[-1] == "?":
                    if word[:-1] in str(kanjiObj.meaning):
                        found.append(i)
                elif word[-1] == "+":
                    if word[:-1] in str(kanjiObj.meaning).split(' '):
                        found.append(i)
                else:
                    if word == str(kanjiObj.meaning):
                        found.append(i)
            i+=1

        return found


    def story_search(self, primitives):
        results = []
        i=0
        for kanjiObj in self.kanjis:
            found = True
            for p in primitives:
                if kanjiObj.story:
                    if not p.replace("_", " ") in kanjiObj.story:
                        found = False
                else:
                    found = False
            if found:
                results.append(i)
            i+=1
        return results


class LookupCli(cmd.Cmd):
    """ The command line interface (Cli). """

    def __init__(self, kc):
        super().__init__()

        # KanjiCollection
        self.kc = kc

        # ----------- Configure me ----------------

        self.defaultMode = 'nothing'
        self.commandSeparator = "."

        # -----------------------------------------

        self.prompt = "Inpt: "
        self.mode = self.defaultMode

        # dict of modes of the form long_form (don't change): [abbrev/command, description]
        self.modes = { 'nothing': ['n', 'do nothing'], 
                       'copy': ['c', 'Copy'], 
                       'www': ['w', 'Lookup'],
                       'primitive': ['p', 'lookup kanji by primitives']}

    def default(self, line):
        """ Default function that gets called on the input. """
        
        line = line.strip()

        if not line:
            self.emptyline()

        elif line.startswith(self.commandSeparator):
            command = line[1:]
            self.command(command)

        elif self.mode == "primitive":
            self.primitive(line)

        else:
            self.search(line)

    # ----------- Handles ---------------

    def emptyline(self):
        """ Gets called if user presses <ENTER> without providing intput. """
        pass

    def command(self, command):
        """ Gets called if line starts with self.commandSeparator. """

        if command == 'h':
            print("Basic commands: .q (quit), .h (help), .!<command> (run command in shell), .m (print current mode) ")
            print("Available modes: %s" % str(self.modes))
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

        for m in self.modes:
            if command == self.modes[m][0]:
                # ----------- switching not possible ---------------
                if m in ['copy', 'www'] and not os.name == "posix":
                    logging.warning("Mode %s currently only supported for linux." % m)
                    logging.debug("You can adapt the corresponding function in the source code!")
                    return
                if m == 'primitive' and not self.kc.storiesAvailable:
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

    def primitive(self, line):
        candidates = self.kc.story_search(line.split(' '))
        for candidate in candidates:
            kanjiObj = self.kc.kanjiObjFromPos(candidate)
            print("%s: %s" % (kanjiObj.kanji, kanjiObj.meaning))
        return

    def search(self, line):
         # split up segments
        segs = line.split(' ')

        # save current mode to temporarily change mode
        # if the current mode doesn't make sense in the context
        # (e.g. lookup mode if more than one expression was found)
        tmp_mode = self.mode

        # Return line
        ans = ""

        for seg in segs:
            hits = self.kc.search(seg)

            if len(hits) == 0:
                if romkan:
                    ans += romkan.to_hiragana(seg)
                else:
                    ans += seg

            elif len(hits) == 1:
                ans += self.kc.kanjiObjFromPos(hits[0]).kanji

            else:
                self.mode = "nothing"

                if len(segs) == 1:
                    for h in hits:
                        ans += "%s: %s\n" % (self.kc.kanjiObjFromPos(h).kanji, self.kc.kanjiObjFromPos(h).meaning)
                else:
                    ans += str(hits)


        ans = ans.rstrip()
        if colorama:
            print(colorama.Fore.RED + ans + colorama.Fore.RESET)
        else:
            print(ans)

        if self.mode == 'copy':
            copy_to_clipboard(ans)
        elif self.mode == 'www':
            lookup(ans)
        elif self.mode == "nothing":
            pass

        # reset mode
        self.mode = tmp_mode
       

if __name__ == '__main__':

    # >>>>>> Load Data
    kc = KanjiCollection()
    logging.debug("Loading rtk data...")
    kc.updateRTK()
    logging.debug("Loding stories...")
    kc.updateStories()
    logging.debug("Loading done.")
    
    if len(sys.argv) == 1:
        # No argument given > start cli interface
        LookupCli(kc).cmdloop()
    
    else:
        # There were arguments > look them up
        lines = ' '.join(sys.argv[1:]).split(",")
        cli = LookupCli(kc)
        for l in lines:
            l = l.lstrip()    # else it matters whether there is a space in front of the ','
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)
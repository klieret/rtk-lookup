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

# todo: update screenshot
# todo: help
# todo: documentation of primitive mode
# todo: which heisig version are we using?


import os
import os.path
import logging
import csv
import sys
import cmd

# The 'romkan' module is used to convert hiragana to romanji (optional).
# It is available at https://pypi.python.org/pypi/romkan
try:
    import romkan
except ImportError:
    romkan = None
    logger.warning("Romkan module not found. No Support for hiragana.")
    logger.debug("Romkan is available at https://pypi.python.org/pypi/romkan.")

# The 'colorama' module is  used to display colors in a platform independent way (optional). 
# It is available at https://pypi.python.org/pypi/colorama
try:
    import colorama
except ImportError:
    colorama = None
    logger.warning("Colorama module not found. No Support for colors.")
    logger.debug("Colorama is available at https://pypi.python.org/pypi/colorama.")
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
            logger.fatal("File %s (to contain heisig indizes) not found. Exiting." % rtkFile)
            sys.exit(1)
        
        with open(rtkFile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanjiColumn].strip()
                index = row[indexColumn].strip()
                meaning = row[meaningColumn].strip().lower()
                
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
            logger.warning("File %s (contains user stories) not found. Primitive mode will be unavailable." % storyFile)
            self.storiesAvailable = False
            return
        else:
            self.storiesAvailable = True
        
        with open(storyFile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanjiColumn].strip()
                story = row[storyColumn].strip().lower()

                pos = self.posFromKanji(kanji) 
                if pos:
                    self.kanjis[pos].story = story
                else:
                    logger.warning("Could not update story for %s." % kanji)

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

        self.defaultMode = 'default'
        self.commandSeparator = "."

        # "Answers" get indented by this amount of spaces
        self.indent = 4

        # Color of the answers. Empty string: No color     
        self.answerColor = colorama.Fore.RED     

        # -----------------------------------------

        self.mode = self.defaultMode
        self.update_prompt()

        # dict of modes of the form long_form (don't change): [abbrev/command, description]
        self.modes = { 'default': ['d', 'do nothing'], 
                       'copy': ['c', 'Copy'], 
                       'www': ['w', 'Lookup'],
                       'primitive': ['p', 'lookup kanji by primitives']}

    def update_prompt(self):
        """ Updates the prompt (self.promp) based on the mode. """

        self.prompt = "[%s] " % self.mode

    def default(self, line):
        """ Default function that gets called on the input. """
        
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
            ans = self.search(line)
            if ans:
                self.ansPrinter(ans)
            else:
                self.ansPrinter("No result. ")


    def ansPrinter(self, ans):
        """ Prints the Kanji results. A simple print(ans) would do, 
        but wrapping it into a function allows for e.g. coloring or
        indenting. """

        if colorama and self.answerColor:
            print(self.answerColor)
        else:
            print()
        
        lines = ans.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            print(" "*4 + line) 
        
        if colorama:
            print(colorama.Style.RESET_ALL)
        else:
            print()

    # ----------- Handlers ---------------

    def emptyline(self):
        """ Gets called if user presses <ENTER> without providing intput. """
        pass

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
                # ----------- switching not possible ---------------
                if m in ['copy', 'www'] and not os.name == "posix":
                    logger.warning("Mode %s currently only supported for linux." % m)
                    logger.debug("You can adapt the corresponding function in the source code!")
                    return
                if m == 'primitive' and not self.kc.storiesAvailable:
                    logger.warning("No user defined stories available. Mode unavailable.")
                    return
                
                # ----------- switching possible -------------------
                if self.mode == m:
                    logger.info("Mode %s is already active." % self.mode)
                    return
                else:
                    self.mode = m
                    logger.info("Switched to mode %s." % self.mode)
                    self.update_prompt()
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
                    ans += '{'
                    for h in hits:
                        ans += "%s (%s), " % (self.kc.kanjiObjFromPos(h).kanji, self.kc.kanjiObjFromPos(h).meaning)
                    # strip last ', '
                    ans = ans[:-2]
                    ans += '}'

        ans = ans.rstrip()


        if self.mode == 'copy':
            copy_to_clipboard(ans)
        elif self.mode == 'www':
            lookup(ans)
        elif self.mode == "nothing":
            pass

        # reset mode
        self.mode = tmp_mode
       
        return ans


if __name__ == '__main__':

    logger = logging.getLogger("lookup")
    logger.setLevel(logging.DEBUG)
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    if colorama:
        fm = logging.Formatter(colorama.Style.DIM + "%(levelname)s: %(message)s" + colorama.Style.RESET_ALL)
    else:
        fm = logging.Formatter("%(levelname)s: %(message)s")

    sh.setFormatter(fm)
    logger.addHandler(sh)



    # >>>>>> Load Data
    kc = KanjiCollection()
    logger.debug("Loading rtk data...")
    kc.updateRTK()
    logger.debug("Loding stories...")
    kc.updateStories()
    logger.debug("Loading done.")
    
    if len(sys.argv) == 1:
        # No argument given > start cli interface
        LookupCli(kc).cmdloop()
    
    else:
        # There were arguments > look them up
        logger.setLevel(logging.CRITICAL)
        lines = ' '.join(sys.argv[1:]).split(",")
        cli = LookupCli(kc)
        for l in lines:
            l = l.lstrip()    # else it matters whether there is a space in front of the ','
            if not l.startswith('.'):
                print("Output for '%s':" % l)
            cli.default(l)
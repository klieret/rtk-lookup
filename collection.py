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

import os
import os.path
import sys
import csv

global colorama
global logger

from modules import *


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
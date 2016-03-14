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

The database class.
"""

import os
import os.path
import sys
import csv

global colorama
global logger

from modules import *


class Kanji(object):
    """An object of this Class contains a kanji with the corresponding 
    information (index, meaning, story etc.)
    """
    def __init__(self, kanji):
        # todo: default values should be "" not None
        self.kanji = kanji
        self.index = None
        self.meaning = None
        self.story = None

    def __equal__(self, other):
        return self.kanji == other.kanji


class KanjiCollection(object):
    """An object of this Class bundles many Kanji objects.
    """
    def __init__(self):
        # a plain list of Kanji objects
        self.kanjis = []
        # todo: maybe instead of having a list of kanji objects, have lists for all of the csv files rows instead, which makes searching easier and then only combine later on.

        # did we load any stories?
        self.stories_available = False

    # ------------- Load information from files -------------------------------

    def load_file_rtk(self):
        """Load the file that contains the RTK kanji, indizes and meanings.
        """

        # --------- CONFIGURE ME ---------

        rtk_file = "RTK.tsv"
        delimeter = '\t'
        kanji_column = 0
        index_column = 1
        meaning_column = 3

        # --------------------------------
        
        if not os.path.exists(rtk_file):
            logger.fatal("File %s (to contain heisig indizes) not found. Exiting." % rtk_file)
            sys.exit(1)
        
        with open(rtk_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanji_column].strip()
                index = row[index_column].strip()
                meaning = row[meaning_column].strip().lower()
                
                kanji_obj = Kanji(kanji)
                kanji_obj.index = index
                kanji_obj.meaning = meaning

                self.kanjis.append(kanji_obj)

    def load_file_stories(self):
        """Load file that contains the RTK kanji, indizes and meanings.
        """

        # --------- CONFIGURE ME ---------

        story_file = "kanji_stories.tsv"
        delimeter = '\t'
        kanji_column = 0
        story_column = 3

        # --------------------------------
        
        if not os.path.exists(story_file):
            logger.warning("File %s (contains user stories) not found. Primitive mode will be unavailable." %
                           story_file)
            self.stories_available = False
            return
        else:
            self.stories_available = True
        
        with open(story_file, 'r') as csvfile:
            # todo: use unicode normalisation?
            reader = csv.reader(csvfile, delimiter=delimeter)
            for row in reader:
                kanji = row[kanji_column].strip()
                story = row[story_column].strip().lower()

                pos = self.pos_from_kanji(kanji)
                if pos:
                    self.kanjis[pos].story = story
                else:
                    logger.warning("Could not update story for %s." % kanji)

    # ------------- pos <> .... -------------------------------
    # Most functions (e.g. search, etc.) will return the position
    # of the KanjiObj corresponding to the matched kanjis in self.kanjis.

    def kanji_obj_from_pos(self, pos):
        """Returns the kanji belonging to the KanjiObj at position pos 
        in self.kanjis.
        :param pos
        :return None
        """
        return self.kanjis[pos]

    # todo: shouldn't that be search_kanji (also do we ever use that?)
    def pos_from_kanji(self, kanji):
        """Given a kanji, returns the position of the corresponding
        Object of class 'Kanji' in self.kanjis.
        :param kanji
        :return None
        """
        # todo: use enumerate instead
        i = 0
        for kanji_obj in self.kanjis:
            if kanji_obj.kanji == kanji:
                return i
            i += 1

        # if not found:
        return None

    # ------------- Search -------------------------------

    # todo: split up w.r.t. to type of search item >> faster
    def search(self, word):
        """
        Does the actual search.
        :param word: search phrase
        :return: The positions of the matching kanjiObjs in self.kanjis (as a list)
        """

        word = word.replace('_', ' ')
        found = []

        # todo: use enumerate instead
        i = 0
        for kanji_obj in self.kanjis:
            if word.isdigit():
                # searching for RTK index
                if kanji_obj.index == word:
                    found.append(i)
            else:
                if word[-1] == "?":
                    # todo: why call str() here? Default values for all attributes should be "", not None
                    if word[:-1] in str(kanji_obj.meaning):
                        found.append(i)
                elif word[-1] == "+":
                    if word[:-1] in str(kanji_obj.meaning).split(' '):
                        found.append(i)
                else:
                    if word == str(kanji_obj.meaning):
                        found.append(i)
            i += 1

        return found

    def primitive_search(self, primitives):
        results = []
        # todo: use enumerate
        i = 0
        for kanji_obj in self.kanjis:
            found = True
            for p in primitives:
                if kanji_obj.story:
                    if not p.replace("_", " ") in kanji_obj.story:
                        found = False
                else:
                    found = False
            if found:
                results.append(i)
            i += 1
        return results

    # ----------------------------- not yet used ------------------------------

    def kanji_obj_from_kanji(self, kanji):
        """Returns kanji_obj corresponding to kanji $kanji.
        :param kanji
        :return None
        """
        for kanji_obj in self.kanjis:
            if kanji_obj.kanji == kanji:
                return kanji_obj
        # not found:
        return None

    def story_from_kanji(self, kanji):
        """Returns story corresponding to kanji $kanji.
        :param kanji
        :return None
        """
        kanji_obj = self.kanji_obj_from_kanji(kanji)
        if kanji_obj:
            return kanji_obj.story
        else:
            return None

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
    information (index, meaning, story etc).
    """
    def __init__(self, kanji):
        # todo: default values should be "" not None
        self.kanji = kanji
        self.index = ""
        self.meaning = ""
        self.story = ""

    def __equal__(self, other):
        return self.kanji == other.kanji


class KanjiCollection(object):
    """An object of this Class bundles many Kanji objects.
    """
    def __init__(self):
        # a plain list of Kanji objects
        self.kanjis = []

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

    # used to update values in self.kanjis
    def pos_from_kanji(self, kanji):
        """Given a kanji, returns the position of the corresponding
        Object of class 'Kanji' in self.kanjis.
        :param kanji
        :return kanji object or None
        """
        for index, kanji_obj in enumerate(self.kanjis):
            if kanji_obj.kanji == kanji:
                return index

        # if not found:
        return None

    # ------------- Search -------------------------------

    # todo: instead have (word, mode) as parameters and also do '_' replace before. not job of collection
    def search(self, word):
        """
        Does the actual search.
        :param word: search phrase
        :return: The positions of the matching kanjiObjs in self.kanjis (as a list)
        """

        word = word.replace('_', ' ')
        found = []

        if word.isdigit():
            # searching for RTK index
            for kanji_obj in self.kanjis:
                if kanji_obj.index == word:
                    found.append(kanji_obj)

        elif word[-1] == "?":
            sword = word[:-1]
            for kanji_obj in self.kanjis:
                if sword in kanji_obj.meaning:
                    found.append(kanji_obj)

        elif word[-1] == "+":
            sword = word[:-1]
            for kanji_obj in self.kanjis:
                if sword in kanji_obj.meaning.split(' '):
                    found.append(kanji_obj)

        elif word[-1] == "%":
            sword = word[:-1]
            for kanji_obj in self.kanjis:
                is_found = True
                for letter in sword:
                    if not kanji_obj.meaning.count(letter) == sword.count(letter):
                        is_found = False
                if is_found:
                    found.append(kanji_obj)

        else:
            for kanji_obj in self.kanjis:
                if word == kanji_obj.meaning:
                    found.append(kanji_obj)

        return found

    # todo: docstring
    def primitive_search(self, primitives):
        results = []
        for kanji_obj in self.kanjis:
            found = True
            for p in primitives:
                if kanji_obj.story:
                    if not p.replace("_", " ") in kanji_obj.story:
                        found = False
                else:
                    found = False
            if found:
                results.append(kanji_obj)
        return results

    def kanji_obj_from_kanji(self, kanji):
        """Returns kanji_obj corresponding to kanji $kanji.
        :param kanji
        :return None
        """
        pos = self.pos_from_kanji(kanji)
        if pos is not None:
            return self.kanjis[pos]
        else:
            return None
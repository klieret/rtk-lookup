#!/usr/bin/python3
# -*- coding: utf8 -*-

""" The collection/database.
"""

import os
import os.path
import sys
import csv
from typing import List
from rtklookup.log import logger
from rtklookup.config import config
from pkg_resources import resource_stream, resource_filename
import codecs


# todo: set config as a class variable instead of using it as a global variable
class Kanji(object):
    """ An object of this Class contains a kanji with the corresponding
    information (index, keyword, story etc).
    """
    def __init__(self, kanji: str):
        self.kanji = kanji
        self.index = ""
        self.keyword = ""
        self.story = ""

    def __equal__(self, other):
        return self.kanji == other.kanji

    def __str__(self):
        return "<{} object for kanji {}>".format(self.__class__.__name__,
                                                 self.kanji)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.kanji.__hash__()


# todo: shouldn't the loading process maybe be done from outside?
class KanjiCollection(object):
    """An object of this Class bundles sevaral Kanji objects.
    """
    def __init__(self):
        # a plain list of Kanji objects
        self.kanjis = []  # type: List[Kanji]

        # did we load any stories?
        self.stories_available = False

    # ------------- Load information from files -------------------------------

    def load_file_rtk(self):
        try:
            self._load_file_rtk()
        except ValueError:
            logger.critical("Failed to load the kanji database. Exiting.")
            sys.exit(1)

    def _load_file_rtk(self):
        """Load the file that contains the RTK kanji, indizes and keywords.
        """

        # we just raise exceptions and catch them later

        resource = ('rtklookup', 'data/rtk_data.tsv')
        filename = resource_filename(*resource)

        print(filename)
        if not os.path.exists(filename):
            logger.fatal("File %s (meant to contain heisig indizes) "
                         "not found. " % filename)
            raise ValueError

        delim = bytes(config["rtk_data"]["delim"], "utf-8").decode(
            "unicode_escape")

        io = resource_stream(*resource)
        csvfile = codecs.getreader("utf-8")(io)
        reader = csv.reader(csvfile, delimiter=delim)
        for row in reader:
            kanji = row[config.getint("rtk_data", "kanji_column")].strip()
            index = row[config.getint("rtk_data", "index_column")].strip()
            keyword = row[config.getint("rtk_data",
                                        "keyword_column")].strip().lower()

            kanji_obj = Kanji(kanji)
            kanji_obj.index = index
            kanji_obj.keyword = keyword

            self.kanjis.append(kanji_obj)

    def load_file_stories(self):
        try:
            self._load_file_stories()
        except ValueError:
            logger.warning("Could not load stories for kanji.")
            self.stories_available = False
        else:
            self.stories_available = True

    def _load_file_stories(self):
        """Load file that contains the RTK kanji, indizes and keywords.
        """

        if not os.path.exists(config["rtk_stories"]["path"]):
            logger.warning("File %s (contains user stories) not found. "
                           "Primitive mode will be unavailable." %
                           config["rtk_stories"]["path"])
            raise ValueError

        delim = bytes(config["rtk_stories"]["delim"], "utf-8").decode(
            "unicode_escape")

        io = resource_stream('data', 'rtk_data.tsv')
        csvfile = codecs.getreader("utf-8")(io)
        reader = csv.reader(csvfile, delimiter=delim)
        # todo: use unicode normalisation?
        for row in reader:
            kanji = row[config.getint("rtk_stories",
                                        "kanji_column")].strip()
            story = row[config.getint("rtk_stories",
                                        "story_column")].strip().lower()

            pos = self.pos_from_kanji(kanji)
            if pos:
                self.kanjis[pos].story = story

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

    def search(self, word: str):
        """
        Does the actual search.
        :param word: search phrase
        :return: The positions of the matching kanjiObjs in self.kanjis [list]
        """
        if not word:
            return

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
                if sword in kanji_obj.keyword:
                    found.append(kanji_obj)

        elif word[-1] == "+":
            sword = word[:-1]
            for kanji_obj in self.kanjis:
                if sword in kanji_obj.keyword.split(' '):
                    found.append(kanji_obj)

        elif word[-1] == "%":
            sword = word[:-1]
            for kanji_obj in self.kanjis:
                is_found = True
                for letter in sword:
                    if not kanji_obj.keyword.count(letter) == \
                            sword.count(letter):
                        is_found = False
                if is_found:
                    found.append(kanji_obj)

        else:
            for kanji_obj in self.kanjis:
                if word == kanji_obj.keyword:
                    found.append(kanji_obj)
                else:
                    # in case the words consists of kanji
                    for letter in word:
                        if letter == kanji_obj.kanji:
                            found.append(kanji_obj)

        return found

    def primitive_search(self, primitives: List[str]):
        """ Searches for kanji based on primitives.
        :param primitives:
        :return:
        """
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

    def kanji_obj_from_kanji(self, kanji: str):
        """Returns kanji_obj corresponding to kanji $kanji.
        :param kanji
        :return None
        """
        pos = self.pos_from_kanji(kanji)
        if pos is not None:
            return self.kanjis[pos]
        else:
            return None

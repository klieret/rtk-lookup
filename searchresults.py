#!/usr/bin/python3
# -*- coding: utf8 -*-

from modules import romkan
import re
from collection import Kanji
# todo: docstrings


class SearchItem(object):
    """ This type holds a single search query and its results.
    """
    def __init__(self, search_string: str):
        self.search = search_string  # type: str
        self.kanji = []  # type: list[Kanji]
        self.hiragana = ""
        self.wildcards = ['%', '+', '*', '?']
        if romkan:
            self.hiragana = romkan.to_hiragana(self.search)
            no_kana_regex = re.compile("[^\u3040-\u30ff]")
            if no_kana_regex.search(self.hiragana):
                # failure to convert completely
                self.hiragana = ""

    @property
    def is_empty(self):
        """ Empty search string?
        :return:
        """
        return self.search == ""

    @property
    def has_kana(self):
        """ Could we successfully convert to hiragana?
        Note: If romkan module is missing, this will always be False.
        :return:
        """
        return bool(self.hiragana)

    @property
    def has_kanji(self):
        """ Could we find at least one kanji matching the search query?
        :return:
        """
        return bool(self.kanji)

    @property
    def is_unique(self):
        """ Returns true if there are no more than one kanjis that match the
        search query. Note: Therefore this function will return True, whenever there
        are no kanji found at all and even if we could not even convert to hiragana.
        :return:
        """
        if self.has_kanji:
            return len(self.kanji) == 1
        else:
            return True

    @property
    def is_broken(self):
        """ Returns true if we could neither find a kanji matching the query
        nor convert to kana.
        :return:
        """
        return not self.is_empty and not self.has_kana and not self.has_kanji

    # todo: implement
    @property
    def needs_annotation(self):
        for wc in self.wildcards:
            if wc in self.search:
                return True
        return False

    @property
    def type(self):
        """Type of the item. Note: If conversion to kana was successfull but we
        also found kanji, "kanji" is returned.
        :return: "kanji" "kana" or "broken"
        """
        if self.has_kanji:
            return "kanji"
        elif self.has_kana:
            return "kana"
        elif self.is_broken:
            return "broken"

    def __str__(self):
        return "<SearchItem object for search '{}'>".format(self.search)

    def __repr__(self):
        return self.__str__()


class SearchItemCollection(object):
    """ This class defines a collection of SearchItems. It represents one query
    as given by user input which was then dissected into single queries.
    """
    def __init__(self, search_string: str):
        """
        :param search_string: The whole search query before dissection.
        :return:None
        """
        self.search = search_string
        self.items = []  # type: list[SearchItem]

    @property
    def is_unique(self):
        """Did we get one unique result for every item the user searched for?
        :return:
        """
        for item in self.items:
            if not item.is_unique:
                return False
        return True

    @property
    def multiple_searches(self) -> bool:
        """Did the user search for multiple items?
        :return:
        """
        return len(self.items) >= 2

    @property
    def is_broken(self) -> bool:
        """Could one of the items that the user searched for not be found/converted at all?
        :return:
        """
        for item in self.items:
            if item.is_broken:
                return True
        return False

    @property
    def is_empty(self):
        """Do we have no search items?
        :return:
        """
        return not self.items

    def __contains__(self, item: int):
        return item in self.items

    def __getitem__(self, item: int) -> SearchItem:
        return self.items[item]

#!/usr/bin/python3
# -*- coding: utf8 -*-

""" Classes to hold the results of queries to to the collection.
A query made by the user in the command line user interface is split up
into single words. SearchResultGroup holds the results
of looking up such a single group, while SearchResult (which contains a list of
SeachResultGroups represents the result of the whole search.
"""

from typing import List
import re
from rtklookup.collection import Kanji
import romkan


class SearchResultGroup(object):
    """ This type holds a single search query and its results.
    """
    def __init__(self, search_string: str):
        self.search = search_string  # type: str
        self.kanji = []  # type: List[Kanji]
        self.kana = self.search
        self.wildcards = ['%', '+', '*', '?']
        if not self.has_kana:
            # checking for self.has_kana to avoid converting hiragana
            # and such to kana.
            self.kana = romkan.to_hiragana(self.search)

    @property
    def is_empty(self):
        """ Empty search string?
        :return:
        """
        return self.search == ""

    @property
    def has_kana(self):
        """ Could we successfully convert to hiragana?
        :return:
        """
        if re.search("[^\u3040-\u30ff]", self.kana):
            return False
        else:
            return True

    @property
    def has_kanji(self):
        """ Could we find at least one kanji matching the search query?
        :return:
        """
        return bool(self.kanji)

    @property
    def is_unique(self):
        """ Returns true if there are no more than one kanjis that match the
        search query. Note: Therefore this function will return True,
        whenever there are no kanji found at all and even if we could not
        even convert to hiragana. :return:
        """
        if self.has_kanji:
            return len(self.kanji) == 1
        else:
            return True

    @property
    def is_broken(self):
        """ Returns true if NONE of the following is is true :
        * we can find at least one matching kanji
        * we can convert to kana
        * the query is empty
        :return:
        """
        return not self.is_empty and not self.has_kana and not self.has_kanji

    @property
    def needs_details(self):
        """ Should this SearchGroup be annotated in the details section?
        Returns true if there are several kanji matching the search criteria
        or if the search contained some kind of wildcard character.
        :return:
        """
        if not self.is_unique:
            return True
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
        return "<{} object for search '{}'>".format(self.__class__.__name__,
                                                    self.search)

    def __repr__(self):
        return self.__str__()


class SearchResult(object):
    """ This class defines a collection of SearchGroups. It represents one query
    as given by user input which was then dissected into single queries.
    """
    def __init__(self, search_string: str, mode=None):
        """
        :param search_string: The whole search query before dissection.
        :return:None
        """
        self.search = search_string
        self.groups = []  # type: List[SearchResultGroup]
        self.mode = mode  # the mode which was used for the search

    def copyable_result(self) -> str:
        """If the user is desperate to search for the result online or copy
        it for some similar person, this returns our best guess for such a
        string. A bit similar to resultprinter.first_line but with as few
        formatting as possible.
        :return:
        """
        ret = ""
        for group in self.groups:
            if group.has_kanji:
                if group.is_unique:
                    ret += group.kanji[0].kanji
                else:
                    ret += "({})".format(''.join(
                        [kanji.kanji for kanji in group.kanji]))
            elif group.has_kana:
                ret += group.kana
            else:
                ret += group.search
        return ret

    @property
    def unique_success(self):
        return self.is_broken and not self.is_broken

    @property
    def is_unique(self):
        """Did we get one unique result for every item the user searched for?
        :return:
        """
        for item in self.groups:
            if not item.is_unique:
                return False
        return True

    @property
    def multiple_searches(self) -> bool:
        """Did the user search for multiple items?
        :return:
        """
        return len(self.groups) >= 2

    @property
    def is_broken(self) -> bool:
        """Could one of the items that the user searched for not be
        found/converted at all?
        :return:
        """
        for item in self.groups:
            if item.is_broken:
                return True
        return False

    @property
    def is_single_kanji(self) -> bool:
        """Does the whole query string contains only one kanji
        and nothing else?
        :return:
        """
        return len(self.groups) == 1 and all([g.kanji for g in self.groups])

    @property
    def is_empty(self):
        """Do we have no search items?
        :return:
        """
        return not self.groups

    def __contains__(self, item: int):
        return item in self.groups

    def __getitem__(self, item: int) -> SearchResultGroup:
        return self.groups[item]

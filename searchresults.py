#!/usr/bin/python3
# -*- coding: utf8 -*-

from modules import romkan
import re
from collection import Kanji
# todo: docstrings


class SearchItem(object):
    def __init__(self, search_string: str):
        self.search = search_string
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
        return self.search == ""

    @property
    def has_kana(self):
        return bool(self.hiragana)

    @property
    def has_kanji(self):
        return bool(self.kanji)

    @property
    def is_unique(self):
        if self.has_kanji:
            return len(self.kanji) == 1
        else:
            return True

    @property
    def is_failed(self):
        return not self.is_empty and not self.has_kana and not self.has_kanji

    @property
    def needs_annotation(self):
        for wc in self.wildcards:
            if wc in self.search:
                return True
        return False

    @property
    def type(self):
        if self.has_kanji:
            return "kanji"
        elif self.has_kana:
            return "kana"
        elif self.is_failed:
            return "broken"

    def __str__(self):
        return "<SearchItem object for search '{}'>".format(self.search)

    def __repr__(self):
        return self.__str__()


class SearchItemCollection(object):
    def __init__(self, search_string: str):
        """
        :param search_string:
        :return:
        """
        self.search = search_string
        self.items = []  # type: list[SearchItem]

    @property
    def is_unique(self):
        for item in self.items:
            if not item.is_unique:
                return False
        return True

    @property
    def multiple_searches(self) -> bool:
        return len(self.items) >= 2

    @property
    def is_failed(self) -> bool:
        for item in self.items:
            if item.is_failed:
                return True
        return False

    @property
    def is_empty(self):
        return not bool(self.items)

    def __contains__(self, item: int):
        return item in self.items

    def __getitem__(self, item: int) -> SearchItem:
        return self.items[item]

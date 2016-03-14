#!/usr/bin/python3
# -*- coding: utf8 -*-

# todo: we can use try/except statements instead of defining our own romkan
from modules import romkan
import re
from collection import Kanji

class SearchItem(object):
    def __init__(self, search_string: str):
        self.search = search_string
        self.kanji = []  # type: list[Kanji]
        self.hiragana = ""
        self.wildcards = ['%', '+', '*', '?']
        if romkan:
            self.hiragana = romkan.to_hiragana(self.search)
            no_kana_regex = re.compile("[^\u3040-\u30ff]")
            if no_kana_regex.match(self.hiragana):
                # failure to convert completely
                self.hiragana = ""

    @property
    def is_kana(self):
        return bool(self.hiragana)

    @property
    def is_kanji(self):
        return bool(self.kanji)

    @property
    def is_unique(self):
        return len(self.kanji) == 1

    @property
    def is_failed(self):
        return not self.is_kana and not self.is_unique

    @property
    def needs_annotation(self):
        for wc in self.wildcards:
            if wc in self.search:
                return True
        return False


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
    def is_failed(self):
        for item in self.items:
            if item.is_failed:
                return True
        return False

    def __contains__(self, item: SearchItem):
        return item in self.items

    def __getitem__(self, item: SearchItem):
        return self.items[item]
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

Utility functions to copy things to the clipboard, look them up in the internet etc.
"""

import os


def copy_to_clipboard(clip: str) -> int:
    """ Copies argument to clipboard.
    :param clip: The text to look up.
    :return 0 for success, otherwise a number != 0
    """
    # Check if we are running on linux:
    success = 1
    if os.name == "posix":
        success = os.system("echo '%s' | xclip -selection c" % clip)
    else:
        raise NotImplemented
    return success


def lookup(clip: str) -> int:
    """ Looks up phrase in the www
    :param clip: The text to look up.
    :return 0 for success, otherwise a number != 0
    """
    # Check if we are running on linux:
    success = 1
    if os.name == "posix":
        success = os.system("firefox http://tangorin.com/general/dict.php?dict=general\&s=%s &" % clip)
    else:
        raise NotImplemented
    return success


class CyclicalList(list):
    """ Like a normal list only with the __getitem__ method overwritten
    so that CyclicalList[index] equals CyclicalList[index % len(CyclicalList)],
    i.e. this behaves like a periodic list: CyclicalList([1,2,3]) = [1,2,3,1,2,3,1,2,3,....]
    """
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def __getitem__(self, item: int):
        return list.__getitem__(self, item % len(self))

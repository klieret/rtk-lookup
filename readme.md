# Lookup Kanji by Heisig Keyword or frame number

## Short Description

For people who learn kanji with the book by 
James Heisig ([remembering the kanji](https://en.wikipedia.org/wiki/Remembering_the_Kanji_and_Remembering_the_Hanzi)). 

A little command line interface that allows to look up multiple kanji with 

* The keyword (or parts of it)
* Parts of the mneomic/story
* The frame number

![3.png](https://raw.githubusercontent.com/klieret/readme-files/master/rtk-lookup/scrot_3.png)

## Installation:

Installation with python package manager:

    pip3 install --user --upgrade rtklookup
   
The command line interface can then be started with

    rtk

If this doesn't work, you can use

    python3 -m rtktools

or add ``~/.local/bin/`` to your ``$PATH`` variable.

Installing latest development version:

    git clone https://github.com/klieret/rtk-lookup.git
    cd rtk-lookup
    pip3 install --editable --user .

To search through your own stories/menmonic, you need to supply them via a text file (e.g. download them from [kanji.koohii](https://kanji.koohii.com/)).

## Basic searching
    
    (default) large resist
        大抵
    (default) 107 1832
        大抵
    (default) large 1832
        大抵

If words are not found, they are converted to hiragana if the ```romkan``` module is installed (optional). 
This ```romkan``` module which can be downloaded [here](https://pypi.python.org/pypi/romkan). 

Examples:
    
    (default) large てい
        大てい
    (default) large 抵
        大抵
    (default) large tei
        大てい

You can also lookup english keyword with kanji too

    (default) 譲
        譲: defer
    (default) 図書館
        書: write
        図: map
        館: bldg.

To quit, type ```.q```.

## Modes 

There are four modes (in parenthesis: command to activate mode)

* default (```.d```): Do nothing.
* copy (```.c```): Copy result to clipboard.
* lookup (```.w```): Lookup expression (default: tangorin.com with firefox)
* conditional: Lookup expression if the search gave a unique result
* primitive (```.p```): Try to find kanji by specifying primitives (this requires an additional file that contains all the kanji stories of the user)

The current mode is displayed by the prompt.

If the input matches more than one result, no action will be performed, regardless of the current mode.
    
## More on searching

If a keyword contains a space, substitute ```_```:

    (default) sign_of_the_hog
        亥

```word+``` will look for all keywords of the form "word1 word2 word3" where word matches (exactly) one of the words. 

    (default) fish+
        乙: fish guts
        魚: fish
        鰭: fish fin

    (default) fin+
        鰭

    (default) fish+ thunder
        乙魚鰭雷
        ────────
        乙: fish guts
        魚: fish
        鰭: fish fin


```word?``` will look for all keywords that contain "word":

    (default) fish?
        貝: shellfish
        乙: fish guts
        魚: fish
        漁: fishing
        恣: selfish
        鰭: fish fin

    (default) fin?
        指: finger
        棺: coffin
        緻: fine
        縁: affinity
        精: refined
        済: finish
        婉: well finished
        鰭: fish fin
        
    (default) fish? thunder
        貝乙魚漁恣鰭雷
        ──────────────
        貝: shellfish
        乙: fish guts
        魚: fish
        漁: fishing
        恣: selfish
        鰭: fish fin

You can mix multiple search options:

## Issues, Suggestions, Feature Requests etc.

Open a ticket at [this addon's gitbucket issue page](https://github.com/klieret/rtk-lookup/issues). Suggestions and feature requests are welcome as well!

## Contributors

* [Kilian Lieret](https://github.com/klieret)
* [Kavin Ruengprateepsang](https://github.com/kavinvin)

## License

GNU AGPL, version 3 or later. The list of all kanji by heisig number ```RTK.tsv``` was included in an Anki plugin with copyright Ian Worthington <Worthy.vii@gmail.com>, GNU GPL, version 3 or later.

## History

* 23 Oct 2017: Moved repository to github.
* 05 Aug 2015: Series of bigger changes.
* 31 Mai 2015: First version released.

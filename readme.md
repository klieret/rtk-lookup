# Lookup Kanji by Heisig Keyword or frame number

## Short Description
A little command line interface that allows to look up kanji with the respective heisig keyword or frame number.

![lookup.png](https://bitbucket.org/repo/qe4bg9/images/274375207-lookup.png)

Examples:
    
    inpt: large resist
    大抵
    
    inpt: 107 1832
    大抵
    
    inpt: large 1832
    大抵
   
If words are not found, they are converted to hiragana. This requires the ```romkan``` module which can be downloaded
[here](https://pypi.python.org/pypi/romkan).

Examples:
    
    inpt: large てい
    大てい
    
    inpt: large 抵
    大抵
    
    inpt: large tei
    大てい

To quit, type ```.q```.

## Modes 

There are three modes (in parenthesis: command to activate mode)

* copy (```.c```): Copy result to clipboard.
* lookup (```.w```): Lookup expression (default: tangorin.com with firefox)
* nothing (```.n```): Do nothing.

If more than one match is found, no action will be performed, regardless of the current mode.
The default mode is ```c``` (but this can easily be changed in the source, as well as the commands above).
    
## More on searching

If a keyword contains a space, substitute ```_```:

    inpt: sign_of_the_hog
    亥

```word+``` will look for all keywords of the form "word1 word2 word3" where word matches (exactly) one of the words. If
there are multiple matches, all of them are printed as a list. 

    Inpt: sign+
    [('酉', 'sign of the bird'), ('亥', 'sign of the hog'), ('寅', 'sign of the tiger'), ('辰', 'sign of the dragon'), ('丑', 'sign of the cow'), ('卯', 'sign of the hare'), ('巳', 'sign of the snake')]
    
    Inpt: fish+
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]
    
    Inpt: fish
    魚
    
    Inpt: fin+
    鰭
    
    Inpt: fish+ thunder
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]雷

```word?``` will look for all keywords that contain "word":

    Inpt: Inpt: goi?
    行
    
    Inpt: fish?
    [('貝', 'shellfish'), ('乙', 'fish guts'), ('魚', 'fish'), ('漁', 'fishing'), ('恣', 'selfish'), ('鰭', 'fish fin')]

    Inpt: fish+
    [('乙', 'fish guts'), ('魚', 'fish'), ('鰭', 'fish fin')]

## Installation:

Download the file ```lookup.py```. And run it with ```python3 lookup.py```.

## Issues, Suggestions, Feature Requests etc.
Open a ticket at [this addon's gitbucket issue page](https://bitbucket.org/ch4noyu/anki-addon-reset-all-fields/issues) (prefered method, also works anonymously without login) or send me an [e-mail](mailto:ch4noyu@yahoo.com). German is fine, too. I am not a professional programmer, so feedback on how to improve my code is welcome, too.

## Source
The source is hostet at [this addon's bitbucket page](https://bitbucket.org/ch4noyu/anki-addon-reset-all-fields/).

## Copyright
**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU AGPL, version 3 or later

The list of all kanji by heisig number "RTK.tsv" was included in an Anki plugin with:

**Copyright**: Ian Worthington <Worthy.vii@gmail.com>

**License:** GNU GPL, version 3 or later

## History

* 31 Mai 2015: First version released.
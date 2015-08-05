# Lookup Kanji by Heisig Keyword or frame number

## Short Description
A little command line interface that allows to look up kanji with the respective heisig keyword or frame number.

![lookup.png](https://bitbucket.org/repo/qe4bg9/images/274375207-lookup.png)

Examples:
    
    [default] large resist

        大抵

    [default] 107 1832

        大抵

    [default] large 1832

        大抵

If words are not found, they are converted to hiragana if the ```romkan``` module is installed (optional). 
This ```romkan``` module which can be downloaded [here](https://pypi.python.org/pypi/romkan). 

Examples:
    
    [default] large てい

    大てい

[default] large 抵

    大抵

[default] large tei

    大てい

To quit, type ```.q```.

## Modes 

There are four modes (in parenthesis: command to activate mode)

* default (```.d```): Do nothing.
* copy (```.c```): Copy result to clipboard.
* lookup (```.w```): Lookup expression (default: tangorin.com with firefox)
* primitive (```.p```): Try to find kanji by specifying primitives (this requires an additional file that contains all the kanji stories of the user)

The current mode is displayed by the prompt.

If the input matches more than one result, no action will be performed, regardless of the current mode.
    
## More on searching

If a keyword contains a space, substitute ```_```:

    [default] sign_of_the_hog

        亥

```word+``` will look for all keywords of the form "word1 word2 word3" where word matches (exactly) one of the words. If
there are multiple matches, all of them are printed as a list. 

    [default] sign_of_the_hog

        亥

    [default] sign+

        酉: sign of the bird
        亥: sign of the hog
        寅: sign of the tiger
        辰: sign of the dragon
        丑: sign of the cow
        卯: sign of the hare
        巳: sign of the snake

    [default] fish+

        乙: fish guts
        魚: fish
        鰭: fish fin

    [default] fin+

        鰭

    [default] fish+ thunder

        {乙 (fish guts), 魚 (fish), 鰭 (fish fin)}雷


```word?``` will look for all keywords that contain "word":

    [default] goi?

    行

[default] fish?

    貝: shellfish
    乙: fish guts
    魚: fish
    漁: fishing
    恣: selfish
    鰭: fish fin

[default] fish+

    乙: fish guts
    魚: fish
    鰭: fish fin


## Installation:

Download the file ```lookup.py```. Run it with ```python3 lookup.py```.

## Issues, Suggestions, Feature Requests etc.

Open a ticket at [this addon's gitbucket issue page](https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword/issues?status=new&status=open) (prefered method, also works anonymously without login) or send me an [e-mail](mailto:ch4noyu@yahoo.com). German is fine, too. I am not a professional programmer, so feedback on how to improve my code is welcome, too.

## Source

The source is hostet at [this addon's bitbucket page](https://bitbucket.org/ch4noyu/lookup-kanji-by-heisig-keyword/overview).

## Copyright

**Copyright:** *ch4noyu* (<mailto:ch4noyu@yahoo.com>)

**Licence:** GNU AGPL, version 3 or later

The list of all kanji by heisig number "RTK.tsv" was included in an Anki plugin with:

**Copyright**: Ian Worthington <Worthy.vii@gmail.com>

**License:** GNU GPL, version 3 or later

## History

* 05 Aug 2015: Series of bigger changes.
* 31 Mai 2015: First version released.
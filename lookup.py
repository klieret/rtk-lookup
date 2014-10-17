#!/usr/bin/python3
""" Input: combination of some of the following
            - Heisig's keyword of a kanji (if the keyword contains a space " ",
                write "+" instead)
            - Heisig's number of a kanji
            - other romanji (will be converted to hiragana)
            - :q (quit), :<mode> (switch to another mode)
    Output: Kanji+hiragana. 
    Modes:    
            - n (normal): just copy to clipboard
            - t (tangorin): look up with tangorin"""


import csv
import romkan
import os

# stores all information
kanjis=[]
# stores mode
mode="n"

#load information
with open("RTK.tsv",'r') as csvfile:
    reader=csv.reader(csvfile, delimiter="\t")
    for row in reader:
        kanjis.append(row)    

#looks up $seg in row $row of the $kanji table
def find(seg,row):
    global kanjis
    for kanji in kanjis:
        if str(kanji[row])==seg:
            return kanji[0]
    #if not found: simply convert to hiragana
    return romkan.to_hiragana(seg)

#look up a single segment of input (divided by spaces)
def single(seg):
    if seg.isdigit()==True:
        return(find(seg,1))
    else:
        return(find(seg,3))

while True:
    string=input("Phrase: ")
    if string==":q":
        break
    if string==":n":
        mode="n"
        continue
    if string==":t":
        mode="t"
        continue
    #split up segments
    segs=string.split(' ')
    ans=""
    for seg in segs:
        #for keywords that contain spaces....
        ans+=single(seg.replace('+',' '))
    print(ans)
    if mode=="n": os.system("echo '"+ans+"' | xclip -selection c")
    if mode=="t": os.system("firefox http://tangorin.com/general/dict.php?dict=general\&s="+ans)

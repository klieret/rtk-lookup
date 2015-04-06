#!/usr/bin/python3
""" Input: combination of some of the following
			- Heisig's keyword of a kanji (if the keyword contains a space " ",
				write "+" instead)
		    - "word+" will look for all keywords of the form "word1 word2 word3" where word matches one of the word1,...
			- if you're not sure whether the keyword is "go" or "going", write "go?" it will look for all words that contain "go" 
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
with open("/home/fuchur/Documents/japan/programs/rtk_lookup/RTK.tsv",'r') as csvfile:
	reader=csv.reader(csvfile, delimiter="\t")
	for row in reader:
		kanjis.append(row)	

while True:
	string=input("Phrase: ")
	
	# Commands
	if string==":q":
		break
	if string=="":
		continue
	if string==":n":
		mode="n"
		continue
	if string==":t":
		mode="t"
		continue
	
	# split up segments
	segs=string.split(' ')
	ans=""
	
	for seg in segs:
		found=[]
		if seg.isdigit()==True:
			for kanji in kanjis:
				if str(kanji[1])==seg:
					found.append((kanji[0],kanji[3]))
		else:
			if seg[-1]=="?":
				for kanji in kanjis:
					if seg[:-1] in str(kanji[3]):
						found.append((kanji[0],kanji[3]))
			elif seg[-1]=="+":
				for kanji in kanjis:
					if seg[:-1] in str(kanji[3]).split(' '):
						found.append((kanji[0],kanji[3]))
			else:
				for kanji in kanjis:
					if seg.replace('+',' ')==str(kanji[3]):
						found.append((kanji[0],kanji[3]))
	
		#if not found: simply convert to hiragana
		if found==[]: found.append((romkan.to_hiragana(seg),'?'))
		
		
		tmpNMode=False
		if len(found)==1: ans+=found[0][0]
		if len(found)>1: 
			tmpNMode=True
			ans+=str(found)
		
	
	print(ans)
	if mode=="n" or tmpNMode: os.system("echo '"+ans+"' | xclip -selection c")
	if mode=="t" and not tmpNMode: os.system("firefox http://tangorin.com/general/dict.php?dict=general\&s="+ans)
	


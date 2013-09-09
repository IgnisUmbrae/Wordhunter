import re
import random

from constants import ORDINALS

STR_ANNOUNCE_MOD = "The {} and {} letters must be the same!"

def generate_modifier(word, round_name, involved_letters, difficulty):
	if round_name == "subanag":
		if len(set(involved_letters)) < len(involved_letters): # We have dupes!
			maxpos = int(round(len(involved_letters)/1.5))
			twodupes = [sorted(random.sample(range(maxpos),2))]
		else: twodupes = None
	elif round_name == "onlyhas":
		r = random.randint(0,max(int(round(len(word)/1.5)),3))
		s = r + random.randint(1,2)
		twodupes = [[r,s]]
	else:
		# Find all letters that occur at least twice within the word, logging only their first and second appearances.
		twodupes = [y[0:2] for y in [[i for i in range(len(word)) if word[i] == x] for x in set(word)] if len(y) > 1]
	if twodupes:
		# Purely random choice often forces players to seek extraordinarily long words, so we minimize the forced word length.
		dupe = min(twodupes,key=max)
		regex = re.compile("".join(["^","."*dupe[0],"(.)","."*(dupe[1] - dupe[0] - 1),r"\1"]))
		str = STR_ANNOUNCE_MOD.format(ORDINALS[dupe[0]],ORDINALS[dupe[1]])
	else:
		regex = None
		str = ""
	return regex, str
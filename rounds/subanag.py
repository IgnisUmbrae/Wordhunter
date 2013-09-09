import re
import random

import constants
from formatting import embolden
from tools import discrete_sample

STR_ANNOUNCE = "Find a word that is a subanagram of {}!"

def subanag_regex(word):
	regex = "^"
	letters = set(word)
	for x in letters:
		regex += "(?!.*"+".*".join([x]*(word.count(x)+1))+")"
	regex += "[" + str("".join(letters)) + "]*$"
	return re.compile(regex)

def generate_round(word, difficulty):
	num_letters = random.randint(8,13)
	num_vowels = min(random.randint(3,5),int(round(num_letters/2.5)))
	letters = discrete_sample(constants.VOWEL_FREQS,num_vowels)+discrete_sample(constants.CONS_FREQS,num_letters-num_vowels)
	random.shuffle(letters)
	str = STR_ANNOUNCE.format(embolden("".join(letters)))
	involved_letters = letters
	return subanag_regex(letters), str, involved_letters
import re
import random

import constants
from formatting import embolden, listtostr

STR_ANNOUNCE = "Find a word that uses only the letters {}!"

VOWELS = set(["A","E","I","O","U"])

def generate(word, difficulty):
	#num_letters = random.randint(5,8)
	#num_vowels = min(random.randint(2,3),int(round(num_letters/2.5)))
	#letters = discrete_sample(constants.VOWEL_FREQS,num_vowels)+discrete_sample(constants.CONS_FREQS,num_letters-num_vowels)
	word_letters = set(word)
	num_letters = min(len(word_letters),random.randint(5,8))
	letters = set(random.sample(word_letters,num_letters))
	# Ensure at least two vowels are available so that the chances of insolubility are extremely low.
	if len(letters & VOWELS) < 2:
		used_word_vowels = letters & VOWELS
		unused_vowels = VOWELS - used_word_vowels
		unused_word_vowels = unused_vowels & word_letters
		if len(unused_word_vowels) > 0: letters.add(random.choice(list(unused_word_vowels)))
		else: letters.add(random.choice(list(unused_vowels)))
	regex = re.compile("^["+"".join(letters)+"]*$")
	str = STR_ANNOUNCE.format(listtostr(map(embolden,sorted(letters)),conj="or"))
	return regex, str
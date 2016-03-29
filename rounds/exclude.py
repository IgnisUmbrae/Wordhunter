import re
import random

import constants
from formatting import embolden, listtostr
from tools import discrete_sample, random_partition

STR_ANNOUNCE = "Find a word that uses none of the letters {}!"

LETTERFREQS = ["E","T","A","I","O","N","S","H","R","L","D","C","U","M","W","F","G","Y","P","B","V","K","J","X","Q","Z"]

class roundgenerator():
	def __init__(self):
		pass

	def generate(self, word, words, difficulty):
		num_letters = random.randint(7,9)
		num_vowels = min(random.randint(3,5),int(round(num_letters/2)))
		letters = sorted(set(discrete_sample(constants.VOWEL_FREQS,num_vowels)+discrete_sample(constants.CONS_FREQS,num_letters-num_vowels)))
		#letters = sorted(map(lambda a: LETTERFREQS[a-1],list(set(random_partition(random.randint(1.5*26,3*26))))))
		regex = "^[^"+"".join(letters)+"]*$"
		str = STR_ANNOUNCE.format(listtostr(map(embolden,letters),conj="and"))
		involved_letters = letters
		return re.compile(regex).match, str, involved_letters
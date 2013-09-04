import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that ends in {}!"

def generate(word, difficulty):
	block_length = min(len(word),random.randint(4,5))
	pos = len(word)-block_length
	block = word[pos:pos+block_length]
	regex = re.compile("^.*"+block+"$")
	str = STR_ANNOUNCE.format(embolden(block))
	involved_letters = set(block)
	return regex, str, involved_letters
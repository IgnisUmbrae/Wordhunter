import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that ends with {}!"

def generate(word, difficulty):
	block_length = min(len(word),random.randint(4,5))
	pos = len(word)-block_length
	block = word[pos:pos+block_length]
	regex = re.compile("^.*"+block+"$")
	str = STR_ANNOUNCE.format(embolden(block))
	return regex, str
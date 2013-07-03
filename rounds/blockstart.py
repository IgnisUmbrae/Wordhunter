import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that starts with {}!"

def generate(word, difficulty):
	block_length = min(len(word),random.randint(3,5))
	pos = 0
	block = word[pos:pos+block_length]
	regex = re.compile("^"+block+".*$")
	str = STR_ANNOUNCE.format(embolden(block))
	return regex, str
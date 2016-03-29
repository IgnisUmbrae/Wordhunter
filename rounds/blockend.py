import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that ends in {}!"

class roundgenerator():
	def __init__(self):
		pass

	def generate(self, word, words, difficulty):
		block_length = min(len(word),random.randint(4,5))
		pos = len(word)-block_length
		block = word[pos:pos+block_length]
		regex = re.compile("^.*"+block+"$")
		str = STR_ANNOUNCE.format(embolden(block))
		involved_letters = block
		return regex.match, str, involved_letters
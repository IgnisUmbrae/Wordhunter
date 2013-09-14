import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that contains {}!"

class roundgenerator():
	def __init__(self):
		pass

	def generate(self, word, difficulty):
		block_length = min(len(word),random.randint(3,4))
		pos = random.randint(0,len(word)-block_length)
		block = word[pos:pos+block_length]
		regex = re.compile("^.*"+block+".*$")
		str = STR_ANNOUNCE.format(embolden(block))
		involved_letters = block
		return regex, str, involved_letters
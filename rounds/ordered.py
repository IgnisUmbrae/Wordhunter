import re
import random
from formatting import embolden, listtostr

STR_ANNOUNCE = "Find a word that contains the letters {} in that order!"

def generate_round(word, difficulty):
	block_length = min(len(word),random.randint(4,6))
	block = [list(word)[i] for i in sorted(random.sample(xrange(len(list(word))),block_length))]
	regex = re.compile("^.*"+".*".join(block)+".*$")
	str = STR_ANNOUNCE.format(listtostr(map(embolden,block)))
	involved_letters = block
	return regex, str, involved_letters
import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a word that begins with {} and ends in {}!"

def generate(word, difficulty):
	block_length = min(len(word)-1,random.randint(3,6))
	left_length = random.randint(1,block_length-1)
	right_length = block_length - left_length
	block = (word[0:left_length],word[-1*right_length:])
	regex = re.compile("^"+block[0]+".*"+block[1]+"$")
	str = STR_ANNOUNCE.format(embolden(block[0]),embolden(block[1]))
	involved_letters = set(block[0]+block[1])
	return regex, str, involved_letters
import re
import random

from constants import ALPHABET
from formatting import embolden, listtostr

STR_ANNOUNCE_MOD = "Your word must exclude {}!"

def generate_modifier(word, round_name, involved_letters, difficulty):
	num_letters = random.randint(1,4)
	possible_letters = None
	if round_name in ["blockbeginend","blockend","blockmiddle","blockstart","ordered"]:
		possible_letters = ALPHABET - set(word)
	if not possible_letters:
		regex = None
		str = ""
	else:
		# This picking ought to be done probabilistically according to letter frequency, but until tools.discrete_sample is rewritten this will have to do.
		letters = random.sample(possible_letters,num_letters)
		regex = re.compile("^[^"+"".join(letters)+"]*$")
		str = STR_ANNOUNCE_MOD.format(listtostr(map(embolden,sorted(letters)),conj="and"))
	return regex, str
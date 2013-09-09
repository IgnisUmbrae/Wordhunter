import re
import random

from formatting import embolden, listtostr

STR_ANNOUNCE_MOD = "Your word must include {}!"

def generate_modifier(word, round_name, involved_letters, difficulty):
	num_letters = random.randint(1,2)
	involved_letters = set(involved_letters)
	possible_letters = None
	if round_name in ["blockbeginend","blockend","blockmiddle","blockstart","ordered","onlyhas"]:
		possible_letters = set(word) - involved_letters
	elif round_name == "subanag":
		possible_letters = involved_letters
	if not possible_letters:
		regex = re.compile("^.*$")
		str = ""
	else:
		letters = random.sample(possible_letters,num_letters) if num_letters < len(possible_letters) else list(possible_letters)
		regex = re.compile("^.*(?:"+".*".join(letters)+("|"+".*".join(reversed(letters)) if len(letters) > 1 else "")+").*$")
		str = STR_ANNOUNCE_MOD.format(listtostr(map(embolden,sorted(letters)),conj="and"))
	return regex, str
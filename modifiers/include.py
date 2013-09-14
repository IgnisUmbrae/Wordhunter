import re
import random

from formatting import embolden, listtostr

STR_ANNOUNCE_MOD = "Your word must include {}!"

class modifiergenerator():
	def __init__(self):
		pass

	def generate(self, word, round_name, involved_letters, difficulty):
		num_letters = random.randint(1,2)
		involved_letters = set(involved_letters)
		if round_name in ["blockbeginend","blockend","blockmiddle","blockstart","ordered","onlyhas"]:
			possible_letters = set(word) - involved_letters
		elif round_name == "subanag":
			possible_letters = involved_letters
		else: possible_letters = None
		if possible_letters:
			letters = random.sample(possible_letters,num_letters) if num_letters < len(possible_letters) else list(possible_letters)
			regex = re.compile("^.*(?:"+".*".join(letters)+("|"+".*".join(reversed(letters)) if len(letters) > 1 else "")+").*$")
			str = STR_ANNOUNCE_MOD.format(listtostr(map(embolden,sorted(letters)),conj="and"))
		else:
			regex = re.compile("^.*$")
			str = ""
		return regex, str
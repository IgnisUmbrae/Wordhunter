import re
import random

from constants import NUM_TIMES

STR_ANNOUNCE_MOD = "You must not use any letter more than {}!"

def generate_modifier(word, round_name, involved_letters, difficulty):
	if round_name not in ["anag","subanag"]:
		if round_name == "onlyhas": max_repeats = random.randint(2,3)
		elif round_name == "exclude": max_repeats = random.randint(1,3)
		else: max_repeats = random.randint(1,2)
		regex = re.compile("^(?:([A-Za-z])(?!"+r".*\1"*max_repeats+"))*$")
		str = STR_ANNOUNCE_MOD.format(NUM_TIMES[max_repeats])
	else:
		regex = None
		str = ""
	return regex, str
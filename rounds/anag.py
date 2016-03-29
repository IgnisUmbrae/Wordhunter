import re
import random

import constants
from formatting import embolden

STR_ANNOUNCE = "Find an anagram of {}! Hint: {}."

class roundgenerator():
	def __init__(self):
		pass

	def anag_regex(self, word):
		regex = "^(?=.{"+str(len(word))+"})("
		letters = set(word)
		for x in letters:
			regex += "(?!.*"+".*".join([x]*(word.count(x)+1))+")"
		regex += "[" + str("".join(letters)) + "]*)$"
		return re.compile(regex)

	def generate(self, word, words, difficulty):
		anag = "".join(random.sample(word,len(word)))
		hintamount = max(int(round(len(word)/4)),1)
		r = random.randint(0,hintamount)
		hint = word[:r]+"*"*(len(word)-hintamount)+(word[-1*(hintamount-r):] if r != hintamount else "")
		str = STR_ANNOUNCE.format(embolden(anag),embolden(hint))
		involved_letters = word
		return self.anag_regex(word).match, str, involved_letters
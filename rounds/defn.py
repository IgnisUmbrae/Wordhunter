import os
import re
import random
from formatting import embolden

STR_ANNOUNCE = "Find a noun that means this: {}. Hint: {}."

class roundgenerator():
	def __init__(self):
		with open(os.path.join('data','WN-nouns.txt'),'r') as f:
			self.wn_words = map(lambda x: x.strip(), f.readlines())
		with open(os.path.join('data','WN-nouns-defs.txt'),'r') as f:
			self.wn_defs = map(lambda x: x.strip(), f.readlines())

	def generate(self, word, words, difficulty):
		r = random.randint(0,len(self.wn_words))
		wnword, defn = self.wn_words[r].upper(), self.wn_defs[r]
		hintamount = max(int(round(len(wnword)/4)),1)
		s = random.randint(0,hintamount)
		hint = wnword[:s]+"*"*(len(wnword)-hintamount)+(wnword[-1*(hintamount-s):] if s != hintamount else "")
		str = STR_ANNOUNCE.format(defn,embolden(hint))
		involved_letters = wnword
		regex = re.compile("".join(["^",wnword,"$"]))
		return regex.match, str, involved_letters
import random
import os
import re

from formatting import embolden

# Boggle Master dice
# @ stands in for Qu

dice=[
["@", "B", "Z", "J", "X", "K"],
["R", "R", "G", "V", "W", "O"],
["E", "E", "E", "E", "A", "M"],
["T", "T", "T", "O", "E", "M"],
["P", "L", "E", "T", "I", "C"],
["S", "N", "T", "C", "W", "C"],
["E", "E", "U", "G", "M", "A"],
["O", "O", "N", "W", "U", "T"],
["A", "A", "A", "F", "R", "S"],
["P", "E", "S", "T", "C", "I"],
["D", "D", "R", "O", "L", "N"],
["E", "E", "E", "E", "A", "A"],
["N", "N", "N", "E", "A", "D"],
["S", "Y", "R", "F", "A", "I"],
["S", "Y", "R", "F", "P", "I"],
["O", "O", "O", "T", "T", "U"],
["D", "R", "O", "H", "L", "N"],
["S", "S", "S", "N", "U", "E"],
["H", "H", "O", "T", "D", "N"],
["I", "I", "I", "T", "T", "E"],
["H", "H", "L", "R", "O", "D"],
["I", "I", "C", "E", "T", "L"],
["R", "R", "Y", "H", "I", "P"],
["A", "A", "S", "F", "R", "I"],
["N", "N", "E", "M", "A", "G"]
]

bonus=["@", "U", "K", "L", "M", "I"] # Not currently implemented

STR_ANNOUNCE = "Find a path that spells a word in the following grid! Diagonals are permitted but each square must only be used once!"

class roundgenerator():
	def __init__(self):
		pass

	# With thanks to Darius Bacon for this excellent prefix-tree solution.
	# http://stackoverflow.com/a/750012
		
	def solve(self):
		for y, row in enumerate(self.grid):
			for x, letter in enumerate(row):
				for result in self.extending(letter, ((x, y),)):
					yield result

	def extending(self, prefix, path):
		if prefix in self.words:
			yield (prefix, path)
		for (nx, ny) in self.neighbors(path[-1]):
			if (nx, ny) not in path:
				prefix1 = prefix + self.grid[ny][nx]
				if prefix1 in self.prefixes:
					for result in self.extending(prefix1, path + ((nx, ny),)):
						yield result

	def neighbors(self, (x, y)):
		for nx in range(max(0, x-1), min(x+2, self.ncols)):
			for ny in range(max(0, y-1), min(y+2, self.nrows)):
				yield (nx, ny)
	
	def get_words(self):
		return set(word for (word, path) in self.solve())

	def get_grid(self):
		random.shuffle(dice)
		grid = ["".join(map(random.choice,dice[5*k:5*(k+1)])) for k in range(0,5)]
		return grid

	def format_grid(self, grid):
		return [embolden(" ".join(g).replace("@","Qu")) for g in grid]
	
	def generate(self, randword, words, difficulty):
		self.grid = self.get_grid()
		self.nrows, self.ncols = len(self.grid), len(self.grid[0])
		alphabet = ''.join(set(''.join(self.grid)))
		bogglable = re.compile('['+alphabet+']{3,}$', re.I).match
		self.words = set(word.strip().replace("QU","@") for word in words if bogglable(word.replace("QU","@")))
		self.prefixes = set(word[:i] for word in self.words for i in range(2, len(word)+1))
		validwords = sorted([w.replace("@","QU") for w in self.get_words()])
		validword = lambda x : x in validwords		
		return validword, [STR_ANNOUNCE] + self.format_grid(self.grid), set(alphabet)
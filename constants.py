SCRABBLE_SCORES = {'A':1, 'B':3, 'C':3, 'D':2, 'E':1, 'F':4, 'G':2, 'H':4, 'I':1, 'J':8, 'K':5, 'L':1, 'M':3, 'N':1, 'O':1, 'P':3, 'Q':10, 'R':1, 'S':1, 'T':1, 'U':1, 'V':4, 'W':4, 'X':8, 'Y':4, 'Z':10, 'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4, 'g':2, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1, 'm':3, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1, 's':1, 't':1, 'u':1, 'v':4, 'w':4, 'x':8, 'y':4, 'z':10}

VOWEL_FREQS = [("A",8.2/38.2),("E",12.7/38.2),("I",7.0/38.2),("O",7.5/38.2),("U",2.8/38.2)]
CONS_FREQS = [("B",1.5/57.919),("C",2.8/57.919),("D",4.3/57.919),("F",2.2/57.919),("G",2.0/57.919),("H",6.1/57.919),("J",0.15/57.919),("K",0.77/57.919),("L",4.0/57.919),("M",2.4/57.919),("N",6.7/57.919),("P",1.9/57.919),("Q",0.095/57.919),("R",6.0/57.919),("S",6.3/57.919),("T",9.1/57.919),("V",0.98/57.919),("W",2.4/57.919),("X",0.15/57.919),("Y",2.0/57.919),("Z",0.074/57.919)]

ALPHABET = set([chr(i) for i in range(65,90)])

NUM_TIMES = ["zero times","once","twice","thrice"]
ORDINALS = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth","eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth","eighteenth","nineteenth","twentieth","twenty-first","twenty-second","twenty-third","twenty-fourth","twenty-fifth","twenty-sixth","twenty-seventh","twenty-eighth","twenty-ninth","thirtieth"]

def calc_score(word):
	score = 0
	for l in word:
		score += SCRABBLE_SCORES[l]
	score += len(word)
	return score
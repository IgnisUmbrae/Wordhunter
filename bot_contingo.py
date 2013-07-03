from irc.bot import SingleServerIRCBot
from collections import defaultdict
import operator
import random
import re
import threading
import time

BEAT_VERBS = ["beat", "outdo", "topple", "fell", "oust", "dethrone", "threaten"]
DESTROY_VERBS = ["smashes", "destroys", "wipes the floor with", "trounces", "obliterates", "eviscerates", "disembowels",
				 "mutilates", "vaporizes", "nukes"]
WIN_PHRASE = ["out in front", "in the lead", "in pole position", "leading the pack", "currently winning"]
REGRET_WORDS = ['unfortunately', 'sadly', "probably because you're all idiots", "due to overwhelming incompetence"]
WIN_WORDS = ["triumphed", "excelled", "pwnt y'all", "manifested the Glory of the Most High", "did brilliantly",
			 "achieved greatness", "exceeded teh awesome11"]
LOSE_CLAUSE = ["Trailing behind", "Falling short of the mark", "Not quite good enough", "Doing not so well", 
			    "Losing spectacularly", "Left flailing in the dust"]
EXCLAMATIONS = ["Yes", "Wow", "Thundercats", "Oh my days", "Totes adorbs", "Great", "Oh yayz", "Champion", "Superb",
			     "Booyakasha"]
CHASING_IDIOMS = ["In hot pursuit", "Hoping to catch up", "Trailing behind", "Still in the race"]

SCRABBLE_SCORES = {'A':1, 'B':3, 'C':3, 'D':2, 'E':1, 'F':4, 'G':2, 'H':4, 'I':1, 'J':8, 'K':5, 'L':1, 'M':3, 'N':1, 'O':1,
				   'P':3, 'Q':10, 'R':1, 'S':1, 'T':1, 'U':1, 'V':4, 'W':4, 'X':8, 'Y':4, 'Z':10, 'a':1, 'b':3, 'c':3, 'd':2,
				   'e':1, 'f':4, 'g':2, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1, 'm':3, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1, 's':1,
				   't':1, 'u':1, 'v':4, 'w':4, 'x':8, 'y':4, 'z':10}
# weighted dict for banned letters puzzle:
ALPHABET = {'A':3.0/5, 'B':1.0/3, 'C':1.0/3, 'D':1.0/2, 'E':1.5, 'F':1.0/4, 'G':1.0/2, 'H':1.0/4, 'I':1, 'J':1.0/8,
		    'K':1.0/5, 'L':1, 'M':1.0/3, 'N':1, 'O':4.0/5, 'P':1.0/3, 'Q':1.0/10, 'R':1, 'S':1, 'T':1, 'U':1.0/5, 'V':1.0/4,
		    'W':1.0/4, 'X':1.0/8, 'Y':1.0/14, 'Z':1.0/10}


class WHBot(SingleServerIRCBot):
	def __init__(self, channel, key, nickname, server, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.ROUND_TIME = 40
		self.RESET_TIME = 20
		self.channel = channel
		self.key = key
		self.new_timer = None
		self.end_timer = None
		self.load_assets()
		self.playing = False
		self.guessing = False
		self.limit_stop = True
		self.limit_die = True
		self.limit_setoptions = True
		self.masternicks = ["Horace_Matthews", "contingo", "etotheipi"]
		self.stopped = False
		self.time_reset = False
		self.scores = defaultdict(int)
		self.tally = defaultdict(int)
		self.rounds = None
	
# bot stuff
	
	def load_assets(self):
		f = open('CSW12mw-wh.txt','r')
		self.words = map(lambda x: x.strip(), f.readlines())
		f.close()
		f = open('CSW12mw-wh-scores.txt','r')
		self.scores = map(lambda x: int(x.strip()), f.readlines())
		f.close()
		self.scored_words = dict(zip(self.words, self.scores))

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel,self.key)
	
	def handle_command(self, command, nick, full_msg):
		if command == "whstart":
			if not self.playing:
				self.start_game()
			else:
				self.output("We're already playing, " + nick + ".")
		elif command == "whrounds":
			if self.playing and self.limit_setoptions and nick not in self.masternicks:
				self.output("You're not allowed to do that, " + nick + ".")	
			else:
				self.start_rounds(full_msg)
		elif command == "whstop":
			if self.playing:
				self.stop_game(nick)
			else:
				self.output("We aren't even playing, " + nick + ".")
		elif command in ["die", "DIE", "disconnect", "quit", "leave", "part"]:
		    if self.limit_die == True:
			    if nick in self.masternicks:
				    self.die()
			    else: 
				    self.output("Sorry, you don't have the authority to kill me, " + nick + ".")
		    else:
			    self.die()
		elif command == "score":
			self.score(nick, self.scores, "selfscore")
		elif command == "scores":
			self.score(nick, self.scores, "score")
		elif command == "tally":
			self.score(nick, self.tally, "tally")
		# these commands should really pass control to separate methods
		elif command == "roundtime":
			try:
				new_time = round(float(full_msg.rsplit(' ')[1]))
				if 5 < new_time < 300:
					msg = ("Round time has been changed to " + str(int(new_time)) + " seconds, " + nick + ".")
					if self.limit_setoptions:
						if nick in self.masternicks:
							self.ROUND_TIME = new_time 
							self.output(msg)
						else:
							self.output("You're not allowed to do that, " + nick + ".")							
					else:
							self.ROUND_TIME = new_time
							self.output(msg)
			except Exception:
				pass					
		elif command == "resettime":
			try:
				new_time = round(float(full_msg.rsplit(' ')[1]))
				if 5 < new_time < 300:
					msg = ("Reset time has been changed to " + str(int(new_time)) + " seconds, " + nick + ".")
					if self.limit_setoptions:
						if nick in self.masternicks:
							self.RESET_TIME = new_time 
							self.output(msg)
						else:
							self.output("You're not allowed to do that, " + nick + ".")
					else:
							self.RESET_TIME = new_time
							self.output(msg)
			except Exception:
				pass		
			
	def on_pubmsg(self, c, e):
		nick = e.source.nick
		text = e.arguments[0]
		if text[0] == '!': 							#it's a command
			command = text.rsplit(' ')[0][1:]
			self.handle_command(command, nick, e.arguments[0])
		else:
			if self.playing and self.guessing:
				word = text.rsplit(' ')[0]
				self.submit_word(word, nick)
		return
	

# score stuff

	def score(self, nick, dic, mode):
		if len(dic) == 0:
			if mode == "tally":
				self.output("No one's won any games yet, " + nick + ".")
				return
			else:
				self.output("No one's won any rounds yet, " + nick + ".")
				return
		player_order = sorted(dic, key=dic.get, reverse = True)
		maxpoints = dic[player_order[0]]
		pnt_var = " point" if maxpoints==1 else " points"
		leaders = [player for (player, value) in dic.items() if value == maxpoints]
		if mode == "selfscore":
			if dic[nick] == 0:
				self.output("You haven't won any points, " + nick + "!")
			else:
				if nick in leaders:
					leaders = list(set(leaders) - {nick})
					if len(leaders) == 0:
						self.output("You're " + random.choice(WIN_PHRASE) + " with " + str(maxpoints) +
								    pnt_var + ", " + nick + "!")
					else:
						tied_sig = "both" if len(leaders) == 1 else "each"
						self.output(nick + ", you're tied in the lead with " + self.concat_players(leaders) + ". You " +
								    tied_sig + " have " + str(maxpoints) + pnt_var + "!")
				else:
					pnt_var = " point" if dic[nick]==1 else " points"
					pnt_var2 = " point" if (maxpoints - dic[nick]) == 1 else " points"
					lead_verb = "has" if len(leaders) == 1 else "have"
					self.output("You have " + str(dic[nick]) + pnt_var + ", " + nick + ". That's " + 
							    str(maxpoints - dic[nick]) + pnt_var2 +
							    " behind " + self.concat_players(leaders) + ", who " + lead_verb + " the lead position.")
		elif mode in ["tally", "score"]:
			player_order = player_order[len(leaders):]
			lead_verb = " is " if len(leaders)==1 else " are " 
			end_word = "." if len(leaders)==1 else random.choice([" each.", " apiece."])
			start_msg = "Overall scores (for all games played): " if mode=="tally" else "Scores for current game: "
			self.output(start_msg + self.concat_players(leaders) + lead_verb + random.choice(WIN_PHRASE) +
					    " with " + str(maxpoints) + pnt_var + end_word)
			if len(player_order) > 0:
				msg = [player + " with " + str(dic[player]) + 
					   [" point" if dic[player] == 1 else " points"][0] for player in player_order]
				trail_verb = " is " if len(player_order)==1 else " are "
				self.output(random.choice(CHASING_IDIOMS) + trail_verb + self.concat_players(msg) + ".")
		elif mode == "final":
			player_order = player_order[len(leaders):]
			winner_word = leaders[0] if len(leaders)==1 else "They"
			end_word = "." if len(leaders)==1 else random.choice([" each.", " apiece."])
			pnt_var = " point" if maxpoints==1 else " points"
			self.output(self.concat_players(leaders) + " " + random.choice(WIN_WORDS) +
					    random.choice(["!!!!!!!!!!", "!!!"]))
			self.output(winner_word + " won with " + str(maxpoints) + pnt_var + end_word)
			if len(player_order) > 0:
				msg = [player + " with " + str(dic[player]) + 
					   [" point" if dic[player] == 1 else " points"][0] for player in player_order]
				trail_verb = " was " if len(player_order)==1 else " were "
				self.output(random.choice(LOSE_CLAUSE) + trail_verb + self.concat_players(msg) + ".")
			for leader in leaders:
					self.tally[leader] += 1
			self.scores = defaultdict(int)
			self.score("NULL", self.tally, "tally")
					
	def concat_players(self, players):
		if len(players) == 1:
			return players[0]
		if len(players) == 2:
			return(players[0] + " and " + players[1])
		else:
			res = self.concat_players([players[0] + ", " + players[1]] + players[2:])
		return res
	
	def final_scores(self):
		self.output("The game is finished!")
		if len(self.scores) == 0:
			self.output(random.choice(REGRET_WORDS).capitalize() + ", nobody scored any points in that game.")
		else:
			self.score("NULL", self.scores, "final")
	
	
# rounds stuff
	def start_rounds(self, full_msg):
		try:
			rnds = int(full_msg.rsplit(' ')[1])
			if 0 < rnds < 5000:
				self.rounds = rnds
				if self.playing:
					self.output("Number of rounds remaining set to: " + str(rnds))
				else:
					self.start_game()
		except Exception:
			pass
		
	def handle_rounds(self):
		if self.rounds == 0:
			self.rounds = None
			self.final_scores()
		elif self.rounds == 1:
			self.output("There is only one round remaining!")
			self.rounds -= 1			
			self.new_round()
		elif self.rounds > 1:
			self.output("There are " + str(self.rounds) + " rounds remaining.")
			self.rounds -= 1
			self.new_round()
				
# game stuff
	
	def calc_score(self, word):
		score = 0
		for l in word:
			score += SCRABBLE_SCORES[l]
		score += len(word)
		return score
	
	def embolden(self, str):
		return str.upper()
		#return "" + str.upper() + ""
	
	def output(self, text):
		self.connection.privmsg(self.channel, text)
	
	def new_round(self):
		self.guessing = False
		self.time_reset = False
		self.output("New round in 10 seconds...")
		self.new_timer = threading.Timer(10, self.new_puzzle)
		self.new_timer.start()
	
	def end_round(self, new_round=True):
		betterword = self.better_word()
		if self.winningword_score > 0:
			msg = ("Time's up! The winning word was " + self.winningnick + "'s " + self.embolden(self.winningword) + 
                  " for " + str(self.winningword_score) + " points!")
			self.scores[self.winningnick] += 1
			if betterword[1] == self.best_score:
				msg2 = "You also could've had " + betterword[0] + " for a maximum " + str(betterword[1]) + " points."
			else:
				msg2 = "You also could've had " + betterword[0] + " for " + str(betterword[1]) + " points."
		else:
			msg = "Time's up! Nobody submitted a word!"
			msg2 = "You could've had " + betterword[0] + " for " + str(betterword[1]) + " points."
		if new_round:
			self.output(msg)
		if self.playing:
			self.output(msg2)
		if new_round and self.rounds is not 0:
			self.score(random.choice(REGRET_WORDS), self.scores, "score")
		if new_round: 
			if self.rounds is not None:
				self.handle_rounds()
			else:
				self.new_round()
		if not new_round:
			self.final_scores()
	
	def strlistify(self, list):
		return ", ".join(list[:-1]) + " and " + list[-1]
	
	def time_warning(self):
		if self.time_left() == 1:
			msg = "1 second left!"
		else:
			msg = str(self.time_left()) + " seconds left!"
		return msg
		
	def time_warning_2(self):
		return "Time remaining reset to " + str(self.RESET_TIME) + " seconds!"
	
	def time_left(self):
		if self.time_reset == False:
			return int(round(self.ROUND_TIME - (time.time() - self.start_time)))  
		if self.time_reset == True:
			return int(round(self.RESET_TIME - (time.time() - self.start_time)))
		
	def start_end_timer(self):
		if self.end_timer:
			self.end_timer.cancel()
		self.end_timer = threading.Timer(self.ROUND_TIME, self.end_round)
		self.end_timer.start()
		self.start_time = time.time()
		self.time_reset = False
    
	def reset_end_timer(self):
		if self.end_timer:
			self.end_timer.cancel()
		self.end_timer = threading.Timer(self.RESET_TIME, self.end_round) 
		self.end_timer.start()
		self.start_time = time.time()
		self.time_reset = True
	
	def submit_word(self, word, nick):
		word = re.sub('[^a-zA-Z]','',word).upper()
		if word in self.best_words:
			msg = ("Congratulations, " + nick + "! You found one of the highest-scoring words, " + self.embolden(word) + 
			      ", worth " + str(self.scored_words[word]) + " points!")
			self.scores[nick] += 1
			self.output(msg)
			self.end_timer.cancel()
			if self.rounds is not None:
				self.handle_rounds()
			else:
				self.score("NULL", self.scores, "score")
				self.new_round()
		elif word in self.possible_words:
			score = self.scored_words[word]
			if score > self.winningword_score:
				if self.winningword_score == 0:
					if self.time_left() < self.RESET_TIME:
						msg = (random.choice(EXCLAMATIONS) + "! " + self.embolden(word) + " fits perfectly for " +
							   str(score) + " points! " + self.time_warning_2())
						self.reset_end_timer()
					else:
						msg = (random.choice(EXCLAMATIONS) + "! " +  self.embolden(word) + " fits perfectly for " + 
							   str(score) + " points! " + self.time_warning())
				elif nick == self.winningnick:
					msg = (random.choice(EXCLAMATIONS) + "! " +  self.embolden(word) + " fits even better for " + 
						   str(score) + " points! " + self.time_warning())
				else:
					if self.time_left() < self.RESET_TIME:
						msg = (random.choice(EXCLAMATIONS) + "! " +  self.embolden(word) + " (" + str(score) + 
							   " points) " + random.choice(DESTROY_VERBS) + " " + self.winningnick + "'s " + 
							   self.embolden(self.winningword) + " (" + str(self.winningword_score) + " points)! " +
							   self.time_warning_2())
						self.reset_end_timer()
					else:
						msg = (random.choice(EXCLAMATIONS) + "! " +  self.embolden(word) + " (" + str(score) +
							   " points) " + random.choice(DESTROY_VERBS) + " " + self.winningnick + "'s " + 
							   self.embolden(self.winningword) + " (" + str(self.winningword_score) + 
							   " points)! " + self.time_warning())
				self.winningword = word
				self.winningword_score = score
				self.winningnick = nick
			else:
				if word == self.winningword:
					msg = "You can't beat a word with itself, " + nick + "!"
				else:
					if nick == self.winningnick:
						fragment = "improve on your"
					else:
						fragment = random.choice(BEAT_VERBS) + " " + self.winningnick + "'s"
					msg = ("Nope! " + self.embolden(word) + " (" + str(score) + " points) doesn't " + fragment + " " +
					      self.embolden(self.winningword) + " (" + str(self.winningword_score) + " points)! " +
					      self.time_warning())
			self.output(msg)
			
	def better_word(self):
		# Find all words with a higher score minimally better than the winning one, and return a random one.
		for c in reversed(self.sorted_possible_scored_words):
			if c[1] > self.winningword_score:
				next_best_score = c[1]
				break
		next_best_pairs = [x for x in self.sorted_possible_scored_words if x[1] == next_best_score]
		return random.choice(next_best_pairs)
		
# Puzzle types:
# 0: contains block anywhere
# 1: contains block at beginning
# 2: contains block at end
# 3: contains blocks at beginning and end
# 4: contains letters in given order (no contiguity requirement)
# 5: doesn't contain given letters
	
	def new_puzzle(self):
		self.winningword = ''
		self.winningword_score = 0
		self.winningnick = ''
		
		self.puzzle_type = random.randint(0,6)
		randword = random.choice(self.words)
		if self.puzzle_type in [0,1,2]:
			if self.puzzle_type == 0:
				block_length = min(len(randword), random.randint(3,4))
				pos = random.randint(0, len(randword) - block_length)
				reprefix = "^.*"
				resuffix = ".*$"
			elif self.puzzle_type == 1:
				block_length = min(len(randword), random.randint(3,5))
				pos = 0
				reprefix = "^"
				resuffix = ".*$"
			elif self.puzzle_type == 2:
				block_length = min(len(randword), random.randint(4,5))
				pos = len(randword) - block_length
				reprefix = "^.*"
				resuffix = "$"
			block = randword[pos:pos + block_length]
			self.regex = re.compile(reprefix + block + resuffix)
		elif self.puzzle_type == 3:
			block_length = random.randint(3,6)
			left_length = random.randint(1,block_length-1)
			right_length = block_length - left_length
			block = (randword[0:left_length], randword[-1 * right_length:])
			self.regex = re.compile("^" + block[0] + ".*" + block[1] + "$")
		elif self.puzzle_type == 4:
			block_length = min(len(randword),random.randint(4,6))
			randword_list = list(randword)
			block = [randword_list[i] for i in sorted(random.sample(xrange(len(randword_list)), block_length))]
			self.regex = re.compile("^.*" + ".*".join(block) + ".*$")
		elif self.puzzle_type in [5,6]:
			alphabet = ALPHABET.items()
			block = ''.join(self.multiple_choice(alphabet, random.randint(5,8)))
			self.regex = re.compile('^[^' + block + ']+$')
			randword = "no random seed word for this puzzle type"
		# catch situations where no words exist for banned letters in puzzle type 5
		try:
			self.possible_words = filter(self.regex.match, self.words)
			print randword, str(self.puzzle_type), block, len(self.possible_words)
			self.possible_scored_words = dict((k,v) for k, v in self.scored_words.items() if self.regex.match(k))
			self.sorted_possible_scored_words = sorted(self.possible_scored_words.iteritems(), 
													   key=operator.itemgetter(1), reverse=True)
			self.best_score = self.sorted_possible_scored_words[0][1]
			self.best_words = [k for k, v in self.possible_scored_words.items() if v == self.best_score]
			
			self.start_end_timer()
			
			self.guessing = True
			
			self.announce_puzzle(block)
		except Exception:
			self.new_puzzle()
	
	def announce_puzzle(self, block):
		if self.puzzle_type == 0:
			msg = "Find a word which contains " + self.embolden(block) + "!"
		elif self.puzzle_type == 1:
			msg = "Find a word which begins with " + self.embolden(block) + "!"
		elif self.puzzle_type == 2:
			msg = "Find a word which ends with " + self.embolden(block) + "!"
		elif self.puzzle_type == 3:
			msg = ("Find a word which begins with " + self.embolden(block[0]) + " and ends with " 
				   + self.embolden(block[1]) + "!")
		elif self.puzzle_type == 4:
			msg = "Find a word which contains the letters " + self.strlistify(block) + " (in that order)!"
		elif self.puzzle_type in [5,6]:
			msg = "Find a word which doesn't contain the letters " + self.strlistify(block) + "!"
		msg = msg + " You have " + str(int(self.ROUND_TIME)) + " seconds!"
		self.output(msg)
	
	def start_game(self):
		self.playing = True
		self.scores = defaultdict(int)
		if self.rounds is None:
			self.output("Wordhunter is starting!")
		else:
			self.output(str(self.rounds) + " rounds of Wordhunter are starting now!")
			self.rounds -= 1
		#self.output("For guidance and a command list, see: http://contingo.neocities.org/wordhunt.html")
		self.new_puzzle()
		
	def stop_game(self, nick):
		if self.limit_stop == True:
			if nick in self.masternicks:
				self.rounds = None
				self.stop(nick)
			else: 
				self.output("Sorry, you don't have the authority to stop the game, " + nick)
		else:
			self.rounds = None
			self.stop(nick)
				
	def stop(self, nick):
		self.playing = False
		self.guessing = False
		if self.new_timer:
			self.new_timer.cancel()
		if self.end_timer:
			self.end_timer.cancel()
		self.output("Wordhunter game heartlessly aborted by " + nick + "!")
		self.playing = False
		self.end_round(new_round=False)
		
# functions for puzzle type 5

	def weighted_choice(self, choices):
		total = sum(w for c, w in choices)
		r = random.uniform(0, total)
		upto = 0
		for c, w in choices:
			if upto + w > r:
				return c
			upto += w	   
	      
	def multiple_choice(self, choices, number):
		banned_letters = set()
		while len(banned_letters) < number:
			banned_letters.add(self.weighted_choice(choices))
		return banned_letters

def main():
	#bot = WHBot('#dnbgam0rs', 'tehsex.ace', 'geemutime', 'irc.choopa.net', 6667)
	#bot = WHBot('#bottesting', 'none', 'logomunchy', 'chat.freenode.net', 6667)
	bot = WHBot('##logophiles', 'none', 'logomunchy', 'chat.freenode.net', 6667)
	bot.start()

if __name__ == "__main__":
    main()
    


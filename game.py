import random
import re
import threading
import time
import sys
from operator import itemgetter

import cfg, chatter
from formatting import embolden, listtostr

class WHGame():
	def __init__(self):
		self.reset_vars()
	
	def reset_vars(self):
		self.new_timer = None
		self.end_timer = None
		self.playing = False
		self.guessing = False
		self.reset = False
		self.reset_streak()
		self.reset_scores()

	def reset_streak(self):
		self.streak = { "nick" : "", "num" : 0 }
		
	def reset_scores(self):
		self.gamescores = {}
	
	# def output(self,text):
		# self.host.output(text)
	
	def new_round(self):
		self.guessing = False
		self.output(chatter.STR_NEW_ROUND)
		self.new_timer = threading.Timer(cfg.NEW_TIME, self.new_puzzle)
		self.new_timer.start()
	
	def end_round(self,new_round=True):
		betterword = self.better_word()
		if self.winningword_score > 0:
			msg = chatter.STR_WINNING_WORD.format(self.winningnick, embolden(self.winningword), self.winningword_score)
			if betterword[1] == self.best_score: msg2 = chatter.STR_ALSO_MAX.format(*betterword)
			else: msg2 = chatter.STR_ALSO_WORD.format(*betterword)
			streaker = self.winningnick
			self.add_score(self.winningnick,self.winningword_score)
		else:
			msg = chatter.STR_NO_SUBMISSION
			if betterword[1] == self.best_score: msg2 = chatter.STR_EG_MAX.format(*betterword)
			else: msg2 = chatter.STR_EG_WORD.format(*betterword)
			streaker = None
		if new_round: self.output(msg)
		self.output(msg2)
		self.define_word(betterword[0])
		self.handle_streak(streaker)
		self.handle_scores()
		if new_round: self.new_round()
	
	def handle_streak(self, nick=None): # Pass nick=None to reset the streak after an unanswered round.
		if nick != None:
			if self.streak["nick"] == nick:
				self.streak["num"] += 1
				self.output(chatter.STR_ON_STREAK.format(self.streak["nick"],self.streak["num"]))
			else:
				if self.streak["num"] > 1: self.output(chatter.STRF_BEAT_STREAK().format(nick,self.streak["nick"],self.streak["num"]))
				self.streak["nick"] = nick
				self.streak["num"] = 1
		else:
			if self.streak["num"] > 1:
				self.output(chatter.STR_LOSE_STREAK.format(self.streak["nick"],self.streak["num"]))
			self.reset_streak()
	
	def add_score(self, nick, points):
		if nick in self.gamescores: self.gamescores[nick] += points
		else: self.gamescores[nick] = points
	
	def handle_scores(self):
		sorted_scores = sorted(self.gamescores.iteritems(),key=itemgetter(1),reverse=True)
		scorelist = "; ".join([": ".join([x[0],str(x[1])]) for x in sorted_scores])
		self.output("Current scores: " + scorelist)
	
	def time_warning(self):
		return chatter.STR_SECS_LEFT.format(self.time_left()) if self.time_left() > 1 else chatter.STR_ONE_SEC
	
	def time_left(self):
		return int(round(((cfg.RESET_TIME if self.reset else cfg.ROUND_TIME) - (time.time() - self.start_time))))
	
	def new_end_timer(self):
		if self.end_timer: self.end_timer.cancel()
		self.end_timer = threading.Timer(cfg.ROUND_TIME,self.end_round)
		self.end_timer.start()
		self.start_time = time.time()
		self.reset = False
	
	def reset_end_timer(self):
		if self.end_timer: self.end_timer.cancel()
		self.end_timer = threading.Timer(cfg.RESET_TIME,self.end_round)
		self.end_timer.start()
		self.start_time = time.time()
		self.reset = True
	
	def submit_word(self, word, nick):
		word = re.sub('[^a-zA-Z]','',word).upper()
		if re.match('NESS(ES)?$',word):
			self.output(chatter.NO_NESSES.format(nick))
		elif word in self.best_words:
			self.add_score(nick,self.scored_words[word])
			self.output(chatter.STR_GOT_MAX.format(nick,embolden(word),self.scored_words[word]))
			self.define_word(word)
			self.end_timer.cancel()
			self.handle_streak(nick)
			self.handle_scores()
			self.new_round()
		elif word in self.possible_words:
			score = self.scored_words[word]
			if score > self.winningword_score:
				if self.winningword_score == 0:
					msg = chatter.STRF_GOOD_WORD().format(embolden(word),str(score))
					if self.time_left() < cfg.RESET_TIME:
						self.reset_end_timer()
						msg += " " + chatter.STR_TIME_RESET
					else:
						msg += " " + self.time_warning()
				elif nick == self.winningnick:
					msg = chatter.STRF_BEAT_SELF().format(embolden(word),str(score)) + " " + self.time_warning()
				else:
					msg = chatter.STRF_BEAT_OTHER().format(embolden(word),score,self.winningnick,embolden(self.winningword),self.winningword_score) + " " + self.time_warning()
				self.winningword = word
				self.winningword_score = score
				self.winningnick = nick
			else:
				if word == self.winningword: msg = chatter.STR_NO_BEAT_SELF.format(nick)
				else:
					poss = "your" if nick == self.winningnick else (self.winningnick + "'s")
					msg = chatter.STRF_NO_BEAT_OTHER().format(embolden(word),str(score),poss,embolden(self.winningword),str(self.winningword_score)) + " " + self.time_warning()
			self.output(msg)
			
	def better_word(self):
		# Find all words with a higher score minimally better than the winning one, and return a random one.
		for c in reversed(self.sorted_possible_scored_words):
			if c[1] > self.winningword_score:
				next_best_score = c[1]
				break
		next_best_pairs = [x for x in self.sorted_possible_scored_words if x[1] == next_best_score]
		return random.choice(next_best_pairs)
	
	def define_word(self,word):
		if word in self.definitions: self.output(": ".join([word,self.definitions[word]]))
	
	def new_puzzle(self):
		self.winningword = ''
		self.winningword_score = 0
		self.winningnick = ''
		
		difficulty = 0 # Not yet implemented
		randword = random.choice(self.words)
		
		round_name = random.choice(self.roundformats.keys())
		round = self.roundformats[round_name]
		regex, announce, involved_letters = round(randword,difficulty)
		
		self.possible_words = filter(regex.match,self.words)
		if random.randint(1,3) == 1:
			modifier_name = random.choice(self.modifiers.keys())
			modifier = self.modifiers[modifier_name]
			mod_regex, mod_announce = modifier(randword,round_name,involved_letters,difficulty)
			if mod_regex: self.possible_words = filter(mod_regex.match,self.possible_words)
		else:
			mod_announce = ""
			mod_regex = re.compile("^.*$")
		
		# This isn't entirely satisfactory, but it's the obvious way to ensure we always have a soluble puzzle.
		# Casual observation suggests that insoluble puzzles are very rare, so this shouldn't be a problem.
		if len(self.possible_words) == 0:
			print >> sys.stderr, "Puzzle not soluble! Generating another."
			self.new_puzzle()
		else:
			self.possible_scored_words = dict((k,v) for k, v in self.scored_words.items() if (regex.match(k) and mod_regex.match(k)))
			self.sorted_possible_scored_words = sorted(self.possible_scored_words.iteritems(), key=itemgetter(1), reverse=True)
			self.best_score = self.sorted_possible_scored_words[0][1]
			self.best_words = [k for k, v in self.possible_scored_words.items() if v == self.best_score]
			
			self.new_end_timer()
			
			self.guessing = True
			
			self.announce_puzzle(" ".join([announce,mod_announce]) if mod_announce else announce)
	
	def announce_puzzle(self, announce):
		self.output(" ".join([announce,chatter.STR_INIT_TIME]))
	
	def start_game(self):
		self.playing = True
		self.output(chatter.STR_GAME_START)
		self.new_puzzle()
		
	def stop_game(self, nick):
		if self.new_timer:
			self.new_timer.cancel()
		if self.end_timer:
			self.end_timer.cancel()
		self.output(chatter.STR_GAME_STOP.format(nick))
		self.handle_streak(None)
		self.reset_vars()
from irc.bot import SingleServerIRCBot
import operator
import random
import re
import threading
import time
import imp
import glob
import os
import sys

import cfg, chatter
from formatting import embolden

# To do: admin tools, persistent scoring across rounds, !introduction command, permit ties if the word submitted is different (optional extra togglable in cfg.py), abstract all game stuff away to a game class (in a separate file) and add ability to run on multiple servers/channels

class WHBot(SingleServerIRCBot):
	def __init__(self, channel, key, nickname, server, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		print >> sys.stderr, "Initializing"
		self.channel = channel
		self.key = key
		self.reset_vars()
		self.load_assets()
		self.load_rounds()
		self.load_modifiers()
		print >> sys.stderr, "Initialization complete"
	
	# Bot stuff.
	
	def reset_vars(self):
		self.new_timer = None
		self.end_timer = None
		self.playing = False
		self.guessing = False
		self.reset = False
		self.reset_streak()
		
	def reset_streak(self):
		self.streak = { "nick" : "", "num" : 0 }
	
	def load_rounds(self):
		self.roundformats = {}
		roundfiles = glob.glob("rounds\*.py")
		for f in roundfiles:
			name = os.path.basename(f)[:-3]
			if name not in cfg.EXCLUDE_ROUNDS:
				try:
					module = imp.load_source(name, f)
					self.roundformats[name] = module.generate
				except Exception, e:
					print >> sys.stderr, "Error loading round '{}': {}".format(name, e)
				else:
					print "Loaded round format: {}".format(name)
	
	def load_modifiers(self):
		self.modifiers = {}
		modfiles = glob.glob("modifiers\*.py")
		for f in modfiles:
			name = os.path.basename(f)[:-3]
			try:
				module = imp.load_source(name, f)
				self.modifiers[name] = module.generate_mod
			except Exception, e:
				print >> sys.stderr, "Error loading modifier '{}': {}".format(name, e)
			else:
				print "Loaded modifier: {}".format(name)
	
	def load_assets(self):
		print "Loading assets..."
		with open('data\CSW12mw-wh.txt','r') as f:
			print "	...word list"
			self.words = map(lambda x: x.strip(), f.readlines())
		with open('data\CSW12mw-wh-scores.txt','r') as f:
			print "	...scores"
			self.scores = map(lambda x: int(x.strip()), f.readlines())
		with open('data\CSW12-defs.txt','r') as f:
			print "	...definitions"
			self.definitions = dict(map(lambda x: x.strip().split("\t",1),f.readlines()))
		self.scored_words = dict(zip(self.words,self.scores))

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel,self.key)
	
	def handle_command(self, command, nick):
		if command == "whstart":
			if not self.playing: self.start_game()
			else: self.output(chatter.STR_PLAYING.format(nick))
		elif command == "whstop":
			if self.playing: self.stop_game(nick)
			else: self.output(chatter.STR_NOT_PLAYING.format(nick))
	
	def on_pubmsg(self, c, e):
		nick = e.source.nick
		text = e.arguments[0]
		if text[0] == cfg.COMMAND_PREFIX:
			command = text.rsplit(' ')[0][1:]
			self.handle_command(command, nick)
		elif self.playing and self.guessing:
				word = text.rsplit(' ')[0]
				self.submit_word(word, nick)
		return
	
	# Game stuff.
	
	def output(self, text):
		self.connection.privmsg(self.channel, text)
	
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
		else:
			msg = chatter.STR_NO_SUBMISSION
			if betterword[1] == self.best_score: msg2 = chatter.STR_EG_MAX.format(*betterword)
			else: msg2 = chatter.STR_EG_WORD.format(*betterword)
			streaker = None
		if new_round: self.output(msg)
		self.output(msg2)
		self.define_word(betterword[0])
		self.handle_streak(streaker)
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
		if re.match('^.*ness(es)?$',word):
			self.output(chatter.NO_NESSES.format(nick))
		elif word in self.best_words:
			self.output(chatter.STR_GOT_MAX.format(nick,embolden(word),self.scored_words[word]))
			self.define_word(word)
			self.end_timer.cancel()
			self.handle_streak(nick)
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
		
		#regex, announce = self.roundformats[-3](randword,difficulty)
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
			self.sorted_possible_scored_words = sorted(self.possible_scored_words.iteritems(), key=operator.itemgetter(1), reverse=True)
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

def main():
	bot = WHBot(cfg.CHANNEL, cfg.KEY, cfg.NICK, cfg.SERVER, cfg.PORT)
	bot.start()

if __name__ == "__main__":
    main()
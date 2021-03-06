﻿from irc.bot import SingleServerIRCBot
import imp
import glob
import os
import sys

import cfg, chatter
from game import WHGame

# To do: 
# - !repeat to repeat preamble
# - Match-play feature
# - Fix text when someone ties first or second. Seems to happen when someone comes from outside the top 3.
# - Bonus cube in Boggle round
# - Different text for people newly entering the top 3
# - Optional bonus points for getting a maximum (not for anag, defn or rounds with similarly few valid words)
# - Admin tools
# - Make bot reconnect automatically on disconnect, pausing and preserving game state
# - Introduction/rules command
# - Begin dynamic hints with the initially-generated hint
# - Global hint amount adjustment
# - Optional playoffs (first to win a single round) to decide ties, or use other criteria (to be decided)
# - Timed (single-letter?) hints for single-answer rounds (e.g. anag)
# - Permit ties if the word submitted is different (optional extra togglable in cfg.py)
# - Add ability to run on multiple servers/channels, sanity checking (must have at least one round type, cannot pick from empty modifier list, etc.)
# - Add special flags to rounds and modifiers (so they can e.g. opt into dynamic partial hinting)
# - Separate scoring code from game code
# - Redo the -NESS(ES) removal script to be morphologically aware, so that words like LIONESS and WITNESS aren't unfairly excluded.
# - Fix "1 seconds" text with absurdly low round (hence reset) times (1 or 2s)
# - Scoring modifications: stop alerting (but keep scores of) people who haven't submitted words in N rounds (configurable); announce top 3 at set intervals (configurable); command to check score; command to list top scores (within a certain stretch of time).
# - Missing vowels round (in the style of Only Connect)

class WHBot(SingleServerIRCBot, WHGame):
	valid_params = {"n" : "num_rounds", "t" : "round_time"}
	default_params = {"n" : cfg.NUM_ROUNDS, "t" : cfg.ROUND_TIME}
	min_values = {"n" : 0, "t" : 5}

	def __init__(self, channel, key, nickname, server, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		WHGame.__init__(self)
		print "Initializing"
		self.channel = channel
		self.key = key
		self.load_assets()
		self.load_plugins("round")
		self.load_plugins("modifier")
		assert(self.rounds)
		print "Initialization complete"
	
	def load_plugins(self,type):
		types = type+"s"
		setattr(self,types,{})
		roundfiles = glob.glob(os.path.join(types,"*.py"))
		for f in roundfiles:
			name = os.path.basename(f)[:-3]
			if name not in getattr(cfg,"EXCLUDE_"+types.upper()):
				try:
					module = imp.load_source(name, f)
					getattr(self,types)[name] = getattr(module,type+"generator")()
				except Exception, e:
					print >> sys.stderr, "Error loading {} '{}': {}".format(type,name,e)
				else:
					print "Loaded {}: {}".format(type,name)
	
	def load_assets(self):
		print "Loading assets..."
		with open(os.path.join('data','CSW12mw-wh.txt'),'r') as f:
			print "	...word list"
			self.words = map(lambda x: x.strip(), f.readlines())
		with open(os.path.join('data','CSW12mw-wh-scores.txt'),'r') as f:
			print "	...scores"
			self.scores = map(lambda x: int(x.strip()), f.readlines())
		with open(os.path.join('data','CSW12-defs.txt'),'r') as f:
			print "	...definitions"
			self.definitions = dict(map(lambda x: x.strip().split("\t",1),f.readlines()))
		self.scored_words = dict(zip(self.words,self.scores))

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		c.join(self.channel,self.key)
	
	def handle_command(self, command, nick, params):
		if command == cfg.START_COMMAND:
			if not self.playing:
				params = map(lambda s:s.split("=",1),params)
				for p in params:
					if p[0] in WHBot.valid_params:
						try:
							value = int(p[1])
							assert(value >= WHBot.min_values[p[0]])
						except Exception, e: value = WHBot.default_params[p[0]]
						finally: setattr(self,WHBot.valid_params[p[0]],value)
				self.set_reset_time()
				self.start_game()
			else: self.output(chatter.STR_PLAYING.format(nick))
		elif command == cfg.REPEAT_COMMAND:
			if self.playing: self.announce_puzzle(reannounce=True)
		elif command == cfg.STOP_COMMAND:
			if self.playing: self.stop_game(nick)
			else: self.output(chatter.STR_NOT_PLAYING.format(nick))
	
	def on_pubmsg(self, c, e):
		nick = e.source.nick
		text = e.arguments[0]
		splittext = text.split(' ')
		if text[0:len(cfg.COMMAND_PREFIX)] == cfg.COMMAND_PREFIX:
			command = splittext[0][len(cfg.COMMAND_PREFIX):]
			self.handle_command(command, nick, splittext[1:])
		elif self.playing and self.guessing:
			word = splittext[0]
			self.submit_word(word, nick)
		return
		
	def output(self, text):
		self.connection.privmsg(self.channel, text)

def main():
	bot = WHBot(cfg.CHANNEL, cfg.KEY, cfg.NICK, cfg.SERVER, cfg.PORT)
	bot.start()

if __name__ == "__main__":
    main()
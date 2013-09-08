from irc.bot import SingleServerIRCBot
import imp
import glob
import os
import sys

import cfg, chatter
from game import WHGame

# To do: 
# - Admin tools
# - Introduction/rules command
# - Permit ties if the word submitted is different (optional extra togglable in cfg.py)
# - Add ability to run on multiple servers/channels, sanity checking (must have at least one round type, cannot pick from empty modifier list, etc.)
# - Override round time as parameter to whstart
# - Scoring modifications: stop alerting (but keep scores of) people who haven't submitted words in N rounds (configurable); running commentary of changes in position in the top 3; announce top 3 at set intervals; command to check score; command to list top scores (within a certain stretch of time).
# - Combine load_rounds and load_modifiers into a more generic function.

class WHBot(SingleServerIRCBot, WHGame):
	valid_params = {"n" : "num_rounds", "t" : "round_time"}
	default_params = {"n" : cfg.NUM_ROUNDS, "t" : cfg.ROUND_TIME}

	def __init__(self, channel, key, nickname, server, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		WHGame.__init__(self)
		print >> sys.stderr, "Initializing"
		self.channel = channel
		self.key = key
		self.load_assets()
		self.load_rounds()
		self.load_modifiers()
		assert(self.roundformats)
		print >> sys.stderr, "Initialization complete"
		
	def load_rounds(self):
		self.roundformats = {}
		roundfiles = glob.glob(os.path.join("rounds","*.py"))
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
		modfiles = glob.glob(os.path.join("modifiers","*.py"))
		for f in modfiles:
			name = os.path.basename(f)[:-3]
			if name not in cfg.EXCLUDE_MODIFIERS:
				try:
					module = imp.load_source(name, f)
					self.modifiers[name] = module.generate_mod
				except Exception, e:
					print >> sys.stderr, "Error loading modifier '{}': {}".format(name, e)
				else:
					print "Loaded modifier: {}".format(name)
	
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
							assert(value > 0)
						except Exception, e: value = WHBot.default_params[p[0]]
						finally: setattr(self,WHBot.valid_params[p[0]],value)
				self.set_reset_time()
				self.start_game()
			else: self.output(chatter.STR_PLAYING.format(nick))
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
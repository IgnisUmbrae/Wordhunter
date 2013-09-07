from irc.bot import SingleServerIRCBot
import imp
import glob
import os
import sys

import cfg, chatter
from game import WHGame

# To do: admin tools, persistent scoring across rounds, !introduction command, permit ties if the word submitted is different (optional extra togglable in cfg.py), abstract all game stuff away to a game class (in a separate file) and add ability to run on multiple servers/channels, sanity checking (must have at least one round type, cannot pick from empty modifier list, etc.)

class WHBot(SingleServerIRCBot, WHGame):
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
		roundfiles = glob.glob("rounds/*.py")
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
		modfiles = glob.glob("modifiers/*.py")
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
		
	def output(self, text):
		self.connection.privmsg(self.channel, text)

def main():
	bot = WHBot(cfg.CHANNEL, cfg.KEY, cfg.NICK, cfg.SERVER, cfg.PORT)
	bot.start()

if __name__ == "__main__":
    main()
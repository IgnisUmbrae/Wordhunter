import random
import re
import threading
import time
import sys
from operator import itemgetter
from collections import OrderedDict

import cfg, chatter
from formatting import embolden, listtostr

class WHGame():
	def __init__(self):
		self.reset_vars()
	
	def set_default_params(self,num_rounds=cfg.NUM_ROUNDS,round_time=cfg.ROUND_TIME):
		self.num_rounds = num_rounds
		self.round_time = round_time
		self.set_reset_time()
	
	def set_reset_time(self):
		self.reset_time = self.round_time/2
		
	def reset_vars(self):
		self.new_timer = None
		self.end_timer = None
		self.podium_timer = None
		self.round_num = 0
		self.set_default_params()
		self.playing = False
		self.guessing = False
		self.reset = False
		self.reset_streak()
		self.reset_scores()

	def reset_streak(self):
		self.streak = {"nick" : "", "num" : 0 }
		
	def reset_scores(self):
		self.newscores = {}
		self.oldscores = {}
	
	# def output(self,text):
		# self.host.output(text)
	
	def new_round(self):
		self.guessing = False
		if self.round_num == self.num_rounds:
			self.final_scores()
			#self.output(chatter.STR_SCORE_PRELUDE)
			#self.podium_timer = threading.Timer(cfg.FINAL_SCORE_DELAY, self.final_scores)
		else:
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
		bonus = self.handle_streak(streaker)
		self.add_score(self.winningnick,self.winningword_score+bonus)
		if new_round: self.new_round()
	
	def handle_streak(self, nick=None): #Pass nick=None to reset the streak after an unanswered round.
		if nick != None:
			if self.streak["nick"] == nick:
				self.streak["num"] += 1
				if cfg.STREAK_BONUS > 0:
					bonus = cfg.STREAK_BONUS*(self.streak["num"]-1)
					msg = chatter.STR_ON_STREAK_BONUS.format(self.streak["nick"],self.streak["num"],bonus)
				else: msg = chatter.STR_ON_STREAK.format(self.streak["nick"],self.streak["num"])
				self.output(msg)
				return bonus
			else:
				if self.streak["num"] > 1: self.output(chatter.STRF_BEAT_STREAK().format(nick,self.streak["nick"],self.streak["num"]))
				self.streak["nick"] = nick
				self.streak["num"] = 1
		else:
			if self.streak["num"] > 1:
				self.output(chatter.STR_LOSE_STREAK.format(self.streak["nick"],self.streak["num"]))
			self.reset_streak()
		return 0
	
	def merge_scores(self,list):
		merged, used = [], []
		list = sorted(list.iteritems(),key=itemgetter(1),reverse=True)
		for n in range(0,len(list)):
			nick = list[n][0]
			if nick not in used:
				score = list[n][1]
				o, k = [], n
				while k < len(list) and list[k][1] == score:
					used.append(list[k][0])
					o.append(list[k][0])
					k += 1
				merged.append((o,score))
		return merged
	
	def get_top_three(self, mergeds):
		# Calculate the top three, taking ties into account.
		top_three = [mergeds[0:i] for i in range(len(mergeds)+1) if sum(map(lambda x: len(x[0]),mergeds[0:i])) >= 3]
		top_three = top_three[0] if top_three else mergeds
		# Discard those with no score.
		return [x for x in top_three if x[1] > 0]

	def merged_pos(self, nick, mergeds):
		index = [i for i in range(len(mergeds)) if nick in mergeds[i][0]][0]
		merged_pos = sum(map(lambda x: len(x[0]),mergeds[0:index]))
		return merged_pos
	
	def get_rank_changes(self, old_merged, new_merged):
		print old_merged, new_merged
		if len(old_merged) != len(new_merged): return None
		# Those with zero points are ranked -1 for later exclusion.
		changes = [(x,self.merged_pos(x,old_merged) if self.oldscores[x] > 0 else -1,self.merged_pos(x,new_merged) if self.newscores[x] > 0 else -1) for x in self.newscores.keys()]
		# Ignore changes that don't affect the top three in some way.
		return [x for x in changes if (x[1] <= 2 or x[2] <= 2) and not (x[1] == -1 and x[2] == -1)]
	
	def add_score(self, nick, points):
		def co_scorers(nick, mergeds):
			return [x[0] for x in mergeds if nick in x[0][0]][0]
			
		def is_tied(nick, mergeds): return len(co_scorers(nick,mergeds)) > 1

		if nick:
			self.oldscores = dict(self.newscores) #Ensure dict is *copied*
			self.newscores[nick] += points
		
		old_merged = self.merge_scores(self.oldscores)
		new_merged = self.merge_scores(self.newscores)
		rank_changes = self.get_rank_changes(old_merged,new_merged)
		top_three = self.get_top_three(new_merged)
		
		# Potentially good idea: generate a list of possible pieces of commentary and output the highest priority/most important one(s).
		
		
		# if rank_changes:
			# for x in rank_changes:
				# if x[1] == 0:
					# if x[0] == 0: #No change in first place.
						# if topthree[0][0] == nick:
							# if len(topthree) > 1: lead = topthree[0][1] - topthree[1][1]
							# else: lead = topthree[0][1]
							# self.output(chatter.STR_INCREASE_LEAD.format(nick,lead))
						# else: self.output(chatter.STR_STILL_AHEAD.format(topthree[0][0],topthree[0][1]))
					# else: #Someone's taken first place!
						# newleader = topthree[0][0]
						# oldleader = topthree[x[0]][0]
						# self.output(chatter.STRF_TAKES_POS(0).format(newleader))
				# elif x[1] == 1:
					# if x[0] < 1: #First has fallen to second!
						# pass
					# elif x[0] > 1: #Someone's taken second place!
						# pass
				# elif x[1] == 2:
					# if x[0] < 2: #First or second has fallen to third!
						# pass
					# elif x[0] > 2: #Someone's taken third place!
						# pass
				# elif x[1] > 2: #Someone's fallen out of the top three!
					# pass
		
			#self.dump_scores()
	
	def final_scores(self):
		chatters = [chatter.STRF_FIRST_POS,chatter.STRF_SECOND_POS,chatter.STRF_THIRD_POS]
		joint_chatters = [chatter.STRF_JOINT_FIRST_POS,chatter.STRF_JOINT_SECOND_POS,chatter.STRF_JOINT_THIRD_POS]
		new_merged = self.merge_scores(self.newscores)
		top_three = self.get_top_three(new_merged)
		for n in range(len(top_three)):
			nicks = listtostr(top_three[n][0])
			pos = self.merged_pos(top_three[n][0][0],new_merged)
			if len(top_three[n][0]) > 1: chat = joint_chatters[pos]
			else: chat = chatters[pos]
			self.output(chat().format(nicks,self.newscores[top_three[n][0][0]]))
		self.stop_game(nick=None)

	def time_warning(self):
		return chatter.STR_SECS_LEFT.format(self.time_left()) if self.time_left() > 1 else chatter.STR_ONE_SEC
	
	def time_left(self):
		return int(round(((self.reset_time if self.reset else self.round_time) - (time.time() - self.start_time))))
	
	def new_end_timer(self):
		if self.end_timer: self.end_timer.cancel()
		self.end_timer = threading.Timer(self.round_time,self.end_round)
		self.end_timer.start()
		self.start_time = time.time()
		self.reset = False
	
	def reset_end_timer(self):
		if self.end_timer: self.end_timer.cancel()
		self.end_timer = threading.Timer(self.reset_time,self.end_round)
		self.end_timer.start()
		self.start_time = time.time()
		self.reset = True
	
	def submit_word(self, word, nick):
		if nick not in self.newscores: self.newscores[nick] = 0 #Mark the submitter as having submitted a word (for scoring purposes).
		word = re.sub('[^a-zA-Z]','',word).upper()
		if re.match('NESS(ES)?$',word):
			self.output(chatter.NO_NESSES.format(nick))
		elif word in self.best_words:
			self.output(chatter.STR_GOT_MAX.format(nick,embolden(word),self.scored_words[word]))
			self.define_word(word)
			self.end_timer.cancel()
			bonus = self.handle_streak(nick)
			self.add_score(nick,self.scored_words[word]+bonus)
			self.new_round()
		elif word in self.possible_words:
			score = self.scored_words[word]
			if score > self.winningword_score:
				if self.winningword_score == 0:
					msg = chatter.STRF_GOOD_WORD().format(embolden(word),score)
					if self.time_left() < self.reset_time:
						self.reset_end_timer()
						msg += " " + chatter.STR_TIME_RESET.format(self.reset_time)
					else:
						msg += " " + self.time_warning()
				elif nick == self.winningnick:
					msg = chatter.STRF_BEAT_SELF().format(embolden(word),score) + " " + self.time_warning()
				else:
					msg = chatter.STRF_BEAT_OTHER().format(embolden(word),score,self.winningnick,embolden(self.winningword),self.winningword_score) + " " + self.time_warning()
				self.winningword = word
				self.winningword_score = score
				self.winningnick = nick
			else:
				if word == self.winningword: msg = chatter.STR_NO_BEAT_SELF.format(nick)
				else:
					poss = "your" if nick == self.winningnick else (self.winningnick + "'s")
					msg = chatter.STRF_NO_BEAT_OTHER().format(embolden(word),score,poss,embolden(self.winningword),self.winningword_score) + " " + self.time_warning()
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
		if cfg.MODIFIER_CHANCE > 0 and random.randint(1,cfg.MODIFIER_CHANCE) == 1:
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
			self.round_num += 1
			self.possible_scored_words = dict((k,v) for k, v in self.scored_words.items() if (regex.match(k) and mod_regex.match(k)))
			self.sorted_possible_scored_words = sorted(self.possible_scored_words.iteritems(), key=itemgetter(1), reverse=True)
			self.best_score = self.sorted_possible_scored_words[0][1]
			self.best_words = [k for k, v in self.possible_scored_words.items() if v == self.best_score]
			
			self.new_end_timer()
			
			self.guessing = True
			
			self.announce_puzzle(" ".join([announce,mod_announce]) if mod_announce else announce)
	
	def announce_puzzle(self, announce):
		if self.round_num == self.num_rounds: round_announce = chatter.STR_ROUND_FINAL
		else: round_announce = chatter.STR_ROUND_NUM.format(self.round_num,self.num_rounds)
		self.output(" ".join([round_announce,announce,chatter.STR_INIT_TIME.format(self.round_time)]))
	
	def start_game(self):
		self.playing = True
		self.output(chatter.STR_GAME_START.format(self.num_rounds))
		self.new_puzzle()
		
	def stop_game(self, nick=None): #Pass nick=None to end the game naturally.
		if self.new_timer: self.new_timer.cancel()
		if self.end_timer: self.end_timer.cancel()
		if nick: self.output(chatter.STR_GAME_STOP.format(nick))
		self.reset_vars()
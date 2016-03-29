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
	
	def set_default_params(self,num_rounds=cfg.NUM_ROUNDS,round_time=cfg.ROUND_TIME):
		self.num_rounds = num_rounds
		self.round_time = round_time
		self.set_reset_time()
	
	def set_reset_time(self):
		self.reset_time = self.round_time/2
		
	def reset_vars(self):
		self.new_timer = None
		self.end_timer = None
		#self.podium_timer = None
		self.round_num = 0
		self.set_default_params()
		self.playing = False
		self.guessing = False
		self.reset = False
		self.reset_streak()
		self.reset_scores()

	def reset_streak(self):
		self.streak = {"nick" : "", "num" : 0}
		
	def reset_scores(self):
		self.newscores = {}
		self.oldscores = {}
	
	# def output(self,text):
		# self.host.output(text)
	
	def new_round(self):
		self.guessing = False
		if self.round_num == self.num_rounds:
			self.final_scores()
			self.stop_game(nick=None)
			#self.output(chatter.STR_SCORE_PRELUDE)
			#self.podium_timer = threading.Timer(cfg.FINAL_SCORE_DELAY, self.final_scores)
		else:
			if self.num_rounds > 0: message = chatter.STR_NEW_ROUND
			else: message = chatter.STR_NEW_ROUND_UNLIMITED
			self.output(message)
			self.new_timer = threading.Timer(cfg.NEW_TIME, self.new_puzzle)
			self.new_timer.start()
	
	def end_round(self,new_round=True):
		betterword = self.better_word()
		if self.winningword_score > 0:
			msg = chatter.STR_WINNING_WORD.format(self.winningnick, self.winningword, self.winningword_score)
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
		if streaker: self.comment_score(self.winningnick)
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
	
	def merge_data(self,list,pos): #When merging rank changes, use pos=1 for origin, 2 for destination
		merged, used = [], []
		list = sorted(list,key=itemgetter(pos),reverse=True)
		for n in range(0,len(list)):
			nick = list[n][0]
			if nick not in used:
				score = list[n][pos]
				o, k = [], n
				while k < len(list) and list[k][pos] == score:
					used.append(list[k][0])
					o.append(list[k][0])
					k += 1
				merged.append((o,score))
		return merged
	
	def get_top_three(self, mergeds):
		# Calculate the top three, taking joint positions into account.
		top_three = [mergeds[0:i] for i in range(len(mergeds)+1) if sum(map(lambda x: len(x[0]),mergeds[0:i])) >= 3]
		top_three = top_three[0] if top_three else mergeds
		# Discard those with no score.
		return [x for x in top_three if x[1] > 0]

	def merged_pos(self, nick, mergeds):
		index = [i for i in range(len(mergeds)) if nick in mergeds[i][0]][0]
		merged_pos = sum(map(lambda x: len(x[0]),mergeds[0:index]))
		return merged_pos
	
	def get_rank_changes(self, old_merged, new_merged):
		# Those with zero points are ranked +inf for later exclusion.
		changes = [(x,self.merged_pos(x,old_merged) if self.oldscores[x] > 0 else float('inf'),self.merged_pos(x,new_merged) if self.newscores[x] > 0 else float('inf')) for x in self.newscores.keys()]
		# Ignore changes that don't affect the top three in some way.
		return [x for x in changes if x[1] <= 2 or x[2] <= 2]
	
	def get_move_text(self,dir,movers,destposnicks,destpos):
		verb = random.choice(chatter.SYNS_FALL_TO if dir == 0 else chatter.SYNS_RISE_TO)
		verb = verb.format("" if len(movers) > 1 else "s")
		if len(destposnicks) > 1 and destposnicks != movers:
			destposnicks = sorted(set(destposnicks) - set(movers))
			extra = " ".join([" with",listtostr(destposnicks)])
		else: extra = ""
		fragment = " ".join([listtostr(sorted(movers)),verb,chatter.STRF_POS(destpos,bool(extra))])
		return "".join([fragment,extra]) + "!"

	def get_stay_text(self,movers,pos):
		verb = random.choice(chatter.SYNS_KEEP).format("" if len(movers) > 1 else "s")
		return " ".join([listtostr(sorted(movers)),verb,chatter.STRF_POS(pos,len(movers) > 1)]) + "."
	
	def get_strengthen_text(self, winner, pos):
		return chatter.STRF_STRENGTHENS_POS(pos).format(winner)
	
	def add_score(self, nick, points):
		self.oldscores = dict(self.newscores) #Ensure dict is *copied*
		if nick: self.newscores[nick] += points
	
	def comment_score(self,winner):
		def coscorers(nick, mergeds):
			return [x[0] for x in mergeds if nick in x[0]][0]

		if self.round_num != self.num_rounds:
			
			old_merged = self.merge_data(self.oldscores.iteritems(),pos=1)
			new_merged = self.merge_data(self.newscores.iteritems(),pos=1)
			rank_changes = self.get_rank_changes(old_merged,new_merged)

			messages, used = [], []
			if len(rank_changes) == 1 and rank_changes[0][1] == float("inf"): # First score of the game
				message = chatter.STR_FIRST_SCORE.format(rank_changes[0][0])
			else: 
				for x in rank_changes:
					nick = x[0]
					if nick not in used:
						oldconicks, newconicks = coscorers(x[0],old_merged), coscorers(x[0],new_merged)
						movers = [r[0] for r in rank_changes if r[1:] == x[1:]]
						used += movers + newconicks
						if x[1] != x[2] or len(oldconicks) > 1: # Movers and shakers (including those moving out of joint positions)
							dir = int(x[2] <= x[1]) # 1 for upward movement, 0 for downward
							# The first element of these message tuples is the priority (lower=higher priority).
							messages.append((0,x[2],self.get_move_text(dir,movers,newconicks,x[2])))
							used += newconicks
						else: # Sitting pretty
							if len(movers) == 1 and movers[0] == winner:
								messages.append((1,x[2],self.get_strengthen_text(winner,x[1])))
							else: messages.append((2,x[2],self.get_stay_text(movers,x[1])))
				messages = sorted(messages,key=itemgetter(0,1))
				message = " ".join(map(itemgetter(2),messages))
			
			self.output(message)
	
	def final_scores(self):
		self.output(chatter.STR_GAME_OVER)
		chatters = [chatter.STRF_FIRST_POS,chatter.STRF_SECOND_POS,chatter.STRF_THIRD_POS]
		joint_chatters = [chatter.STRF_JOINT_FIRST_POS,chatter.STRF_JOINT_SECOND_POS,chatter.STRF_JOINT_THIRD_POS]
		new_merged = self.merge_data(self.newscores.iteritems(),pos=1)
		top_three = self.get_top_three(new_merged)
		if top_three:
			for n in range(len(top_three)):
				nicks = listtostr(top_three[n][0])
				pos = self.merged_pos(top_three[n][0][0],new_merged)
				if len(top_three[n][0]) > 1: chat = joint_chatters[pos]
				else: chat = chatters[pos]
				self.output(chat().format(nicks,self.newscores[top_three[n][0][0]]))
		else: self.output(chatter.STR_NO_SCORES)

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
		if re.match('NESS(?:ES)?$',word):
			self.output(chatter.NO_NESSES.format(nick))
		elif word in self.best_words:
			if len(self.best_words) > 1:
				maxmsg = chatter.STR_GOT_MAX.format(nick,len(self.best_words),embolden(word),self.scored_words[word])
			else:
				maxmsg = chatter.STR_GOT_MAX_UNIQUE.format(nick,embolden(word),self.scored_words[word])
			self.output(maxmsg)
			self.define_word(word)
			self.end_timer.cancel()
			bonus = self.handle_streak(nick)
			self.add_score(nick,self.scored_words[word]+bonus)
			self.comment_score(nick)
			self.new_round()
		elif word in self.possible_words:
			score = self.scored_words[word]
			if score > self.winningword_score:
				if self.winningword_score == 0:
					msg = chatter.STRF_GOOD_WORD().format(word,score)
					if self.time_left() < self.reset_time:
						self.reset_end_timer()
						msg += " " + chatter.STR_TIME_RESET.format(self.reset_time)
					else:
						msg += " " + self.time_warning()
				elif nick == self.winningnick:
					msg = chatter.STRF_BEAT_SELF().format(word,score) + " " + self.time_warning()
				else:
					msg = chatter.STRF_BEAT_OTHER().format(word,score,self.winningnick,self.winningword,self.winningword_score) + " " + self.time_warning()
				self.winningword = word
				self.winningword_score = score
				self.winningnick = nick
			else:
				if word == self.winningword: msg = chatter.STR_NO_BEAT_SELF.format(nick)
				else:
					poss = "your" if nick == self.winningnick else (self.winningnick + "'s")
					msg = chatter.STRF_NO_BEAT_OTHER().format(word,score,poss,self.winningword,self.winningword_score) + " " + self.time_warning()
			self.output(msg)
		elif cfg.DYNAMIC_HINTS and self.round_name in ["anag","defn"]:
			newindices = set([i for i in range(min(len(word),len(self.answord))) if word[i] == self.answord[i]])
			allindices = newindices | self.hint_indices
			if (newindices - self.hint_indices):
				self.hint_indices = allindices
				partial = "".join([self.answord[i] if i in sorted(allindices) else "?" for i in range(len(self.answord))])
				self.output(chatter.STRF_ANAG_HINT().format(partial))
			
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
		self.hint_indices = set([])
		randword = random.choice(self.words)
		
		#self.round_name = "boggle"
		self.round_name = random.choice(self.rounds.keys())
		round = self.rounds[self.round_name].generate
		validmatch, announce, involved_letters = round(randword,self.words,difficulty)
		self.answord = involved_letters
		
		self.possible_words = filter(validmatch,self.words)
		if cfg.MODIFIER_CHANCE > 0 and random.randint(1,cfg.MODIFIER_CHANCE) == 1:
			modifier_name = random.choice(self.modifiers.keys())
			modifier = self.modifiers[modifier_name].generate
			mod_regex, mod_announce = modifier(randword,self.round_name,involved_letters,difficulty)
			if mod_regex: self.possible_words = filter(mod_regex.match,self.possible_words)
		else:
			mod_announce = ""
			mod_regex = None
		
		# This isn't entirely satisfactory, but it's the obvious way to ensure we always have a soluble puzzle.
		# Casual observation suggests that insoluble puzzles are uncommon, so this shouldn't be a problem.
		if len(self.possible_words) == 0:
			print >> sys.stderr, "Puzzle not soluble! Generating another."
			self.new_puzzle()
		else:
			self.round_num += 1
			if mod_regex:
				self.possible_scored_words = dict((k,v) for k, v in self.scored_words.items() if (validmatch(k) and mod_regex.match(k)))
			else:
				self.possible_scored_words = dict((k,v) for k, v in self.scored_words.items() if validmatch(k))
			self.sorted_possible_scored_words = sorted(self.possible_scored_words.iteritems(), key=itemgetter(1), reverse=True)
			self.best_score = self.sorted_possible_scored_words[0][1]
			self.best_words = [k for k, v in self.possible_scored_words.items() if v == self.best_score]
			
			self.new_end_timer()
			
			self.guessing = True
			
			if not isinstance(announce, list):
				self.announce_text = " ".join([announce,mod_announce]) if mod_announce else announce
			else:
				self.announce_text = [announce[0] + " " + mod_announce] + announce[1:] if mod_announce else announce
			self.announce_puzzle(reannounce=False)
			
	def announce_puzzle(self,reannounce=False):
		time_text = self.time_warning() if reannounce else chatter.STR_INIT_TIME.format(self.round_time)
		if self.num_rounds == 0: round_announce = chatter.STR_ROUND_NUM_UNLIMITED.format(self.round_num)
		elif self.round_num == self.num_rounds: round_announce = chatter.STR_ROUND_FINAL
		else: round_announce = chatter.STR_ROUND_NUM.format(self.round_num,self.num_rounds)
		if not isinstance(self.announce_text, list):
			self.output(" ".join([round_announce,self.announce_text,time_text]))
		else:
			self.output(" ".join([round_announce,self.announce_text[0],time_text]))
			for x in self.announce_text[1:]: self.output(x)
			
	
	def start_game(self):
		self.playing = True
		if self.num_rounds > 0: message = chatter.STR_GAME_START.format(self.num_rounds)
		else: message = chatter.STR_GAME_START_UNLIMITED
		self.output(message)
		self.new_puzzle()
		
	def stop_game(self, nick=None): #Pass nick=None to end the game naturally.
		if self.new_timer: self.new_timer.cancel()
		if self.end_timer: self.end_timer.cancel()
		if nick: self.output(chatter.STR_GAME_STOP.format(nick))
		if self.num_rounds == 0: self.final_scores()
		self.reset_vars()
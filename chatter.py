import cfg
import random

SYNS_BEAT = ["beat", "outdo", "topple", "fell", "oust"]
SYNS_DESTROYS = ["smashes", "destroys", "wipes the floor with", "trounces", "crushes", "annihilates", "decimates", "obliterates"]
SYNS_DESTROYED = ["smashed", "destroyed", "annihilated", "decimated", "obliterated"]
SYNS_COMPLETELY = ["completely", "utterly", "totally", "absolutely"]
SYNS_YES = ["Yes!", "Nice!"]
SYNS_NO = ["Nope!", "No way!"]

STR_GAME_START = "Wordhunter game starting!"
STR_GAME_STOP = "Wordhunter game heartlessly aborted by {}!"
STR_PLAYING = "We're already playing, {}."
STR_NOT_PLAYING = "We aren't playing, {}."
STR_NO_NESSES = "Sorry, {}, but all words in -ness(es) are banned."
STR_INIT_TIME = "You have {} seconds!".format(cfg.ROUND_TIME)
STR_NEW_ROUND = "New round in {} seconds...".format(cfg.NEW_TIME)
STR_WINNING_WORD = "Time's up! The winning word was {}'s {} for {} points!"
STR_ALSO_WORD = "You also could've had {} for {} points."
STR_ALSO_MAX = "You also could've had {} for a maximum {} points."
STR_EG_WORD = "You could've had {} for {} points."
STR_NO_SUBMISSION = "Time's up! Nobody submitted a word!"
STR_ONE_SEC = "Just one second remaining!"
STR_SECS_LEFT = "{} seconds left!"
STR_TIME_RESET = "Timer reset to {} seconds!".format(cfg.RESET_TIME)
STR_GOT_MAX = "Congratulations, {}! You found one of the highest-scoring words, {}, worth {} points!"
def STRF_GOOD_WORD(): return " ".join([random.choice(SYNS_YES),"{} fits perfectly for {} points!"])
def STRF_BEAT_SELF(): return " ".join([random.choice(SYNS_YES),"{} fits even better for {} points!"])
def STRF_BEAT_OTHER(): return " ".join([random.choice(SYNS_YES),"{} ({} points)",random.choice(SYNS_DESTROYS),"{}'s {} ({} points)!"])
STR_NO_BEAT_SELF = "You can't beat a word with itself, {}!"
def STRF_NO_BEAT_OTHER(): return " ".join([random.choice(SYNS_NO),"{} ({} points) doesn't","beat","{} {} ({} points)!"])
STR_ON_STREAK = "{} is on a winning streak of {}!"
def STRF_BEAT_STREAK(): return " ".join(["{}",random.choice(SYNS_COMPLETELY),random.choice(SYNS_DESTROYED),"{}'s winning streak of {}!"])
STR_LOSE_STREAK = "So ends {}'s winning streak of {}."
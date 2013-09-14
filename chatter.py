import cfg
import random
from constants import ORDINALS

SYNS_YES = ["Yes!", "Nice!"]
SYNS_NO = ["Nope!", "No way!"]

SYNS_BEAT = ["beat", "outdo", "topple", "fell", "oust"]
SYNS_DESTROYS = ["smashes", "destroys", "wipes the floor with", "trounces", "crushes", "annihilates", "decimates", "obliterates"]
SYNS_DESTROYED = ["smashed", "destroyed", "annihilated", "decimated", "obliterated"]
SYNS_COMPLETELY = ["completely", "utterly", "totally", "absolutely"]

SYNS_FALL_TO = ["drop{} to","fall{} to","slip{} to","plummet{} to","get{} knocked down to"]
SYNS_RISE_TO = ["grab{}","take{}","climb{} to","jump{} to"]
SYNS_KEEP = ["remain{} in","keep{} hold of"]

SYNS_SORT_OF = ["Not quite!","Sort of!"]

SYNS_FIRST_POS = ["In first place it's {} with {} points!","{} is the champion with {} points!","{} came out on top with {} points!","{} takes gold with {} points!"]
SYNS_JOINT_FIRST_POS = ["In first place it's {} with {} points apiece!","{} are the champions with {} points apiece!","{} came out on top with {} points each!","{} take gold with {} points each!"]
SYNS_SECOND_POS = ["{} ran a close second with {}.","{} takes silver with {}.","{}'s {} points were only enough for second."]
SYNS_JOINT_SECOND_POS = ["{} both ran a close second with {}.","{} take silver with {} points apiece.","{}'s {} points were only enough for second."]
SYNS_THIRD_POS = ["{} is bringing up the rear with {}.","{} makes do with bronze and {}.","{} managed a mere third with {}."]
SYNS_JOINT_THIRD_POS = ["{} are bringing up the rear with {} points each.","{} make do with bronze and {}.","{} managed a mere third with {} points apiece."]

STR_GAME_START = "{}-round Wordhunter game starting!"
STR_GAME_START_UNLIMITED = "Never-ending Wordhunter game starting!"
STR_GAME_STOP = "Wordhunter game heartlessly aborted by {}!"
STR_PLAYING = "We're already playing, {}."
STR_NOT_PLAYING = "We aren't playing, {}."
STR_NO_NESSES = "Sorry, {}, but all words in -ness(es) are banned."
STR_INIT_TIME = "You have {} seconds!"
STR_NEW_ROUND = "Next round in {} seconds...".format(cfg.NEW_TIME)
STR_NEW_ROUND_UNLIMITED = "New round in {} seconds...".format(cfg.NEW_TIME)
STR_ROUND_NUM = "Round {} of {}."
STR_ROUND_NUM_UNLIMITED = "Round {}."
STR_ROUND_FINAL = "Final round!"
#STR_SCORE_PRELUDE = "Stand by for the final scores!"
STR_WINNING_WORD = "Time's up! The winning word was {}'s {} for {} points!"
STR_ALSO_WORD = "You also could've had {} for {} points."
STR_ALSO_MAX = "You also could've had {} for a maximum {} points."
STR_EG_WORD = "You could've had {} for {} points."
STR_EG_MAX = "You could've had {} for a maximum {} points."
STR_NO_SUBMISSION = "Time's up! Nobody submitted a word!"
STR_ONE_SEC = "Just one second remaining!"
STR_SECS_LEFT = "{} seconds left!"
STR_TIME_RESET = "Timer reset to {} seconds!"
STR_GAME_OVER = "Game over! Let's look at the scores..."
def STRF_ANAG_HINT(): return " ".join([random.choice(SYNS_SORT_OF),"Hint:","{}"])
STR_GOT_MAX = "Congratulations, {}! You found one of the highest-scoring words, {}, worth {} points!"
def STRF_GOOD_WORD(): return " ".join([random.choice(SYNS_YES),"{} fits perfectly for {} points!"])
def STRF_BEAT_SELF(): return " ".join([random.choice(SYNS_YES),"{} fits even better for {} points!"])
def STRF_BEAT_OTHER(): return " ".join([random.choice(SYNS_YES),"{} ({} points)",random.choice(SYNS_DESTROYS),"{}'s {} ({} points)!"])
STR_NO_BEAT_SELF = "You can't beat a word with itself, {}!"
def STRF_NO_BEAT_OTHER(): return " ".join([random.choice(SYNS_NO),"{} ({} points) doesn't","beat","{} {} ({} points)!"])
STR_ON_STREAK = "{} is on a winning streak of {}"
STR_ON_STREAK_BONUS = "{} is on a winning streak of {} and receives a bonus of {} points!"
def STRF_BEAT_STREAK(): return " ".join(["{}",random.choice(SYNS_COMPLETELY),random.choice(SYNS_DESTROYED),"{}'s winning streak of {}!"])
STR_LOSE_STREAK = "So ends {}'s winning streak of {}."
def STRF_TAKES_POS(pos): return " ".join(["{}",random.choice(SYNS_TAKES_POS).format(STRF_POS(pos))])
STR_STILL_AHEAD = "{} still leads with {} points!"
STR_INCREASE_LEAD = "{} is now {} points ahead!"
def STRF_FIRST_POS(): return " ".join([random.choice(SYNS_FIRST_POS),"Congratulations!"])
def STRF_SECOND_POS(): return random.choice(SYNS_SECOND_POS)
def STRF_THIRD_POS(): return random.choice(SYNS_THIRD_POS)
def STRF_JOINT_FIRST_POS(): return " ".join([random.choice(SYNS_JOINT_FIRST_POS),"Congratulations!"])
def STRF_JOINT_SECOND_POS(): return random.choice(SYNS_JOINT_SECOND_POS)
def STRF_JOINT_THIRD_POS(): return random.choice(SYNS_JOINT_THIRD_POS)
STR_FIRST_SCORE = "{} draws first blood!"
def STRF_POS(pos,joint=False): return ("joint " if joint else "") + ORDINALS[pos]# + ("" if random.randint(0,1) == 0 else " place")
def STRF_FALL_TO(pos,joint=False): return " ".join(["{}",random.choice(SYNS_FALLS),"to {}!".format(STRF_POS(pos,joint))])
def STRF_HAS_POS(pos,joint=False): return " ".join(["{}","are" if joint else "is",STRF_POS(pos,joint),"with {}!"])
STR_NO_SCORES = "Nobody managed even a single correct answer! What on earth were you all doing?!"
def STRF_STRENGTHENS_POS(pos): return " ".join(["{}","strengthens their {} place position!".format(STRF_POS(pos,joint=False))])
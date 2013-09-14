# Default length of time each round lasts, in seconds. Can be overridden by passing t=# with the start command.
ROUND_TIME = 50
# If the first correct answer submitted is after RESET_TIME seconds, the timer is reset to this value to stop sniping.
RESET_TIME = ROUND_TIME/2
# Length of time (in seconds) to wait between the end of the final round and the announcement of the final scores. (Not currently in use.)
FINAL_SCORE_DELAY = RESET_TIME/2
# Default number of rounds to play each game. Can be overridden by passing n=# with the start command.
NUM_ROUNDS = 15
# Number of times to announce the top scorers each game, distributed evenly over all rounds.
SCORE_ANNOUNCE_NUM = 5
# On average, one in every MODIFIER_CHANCE rounds has a modifier, though implementation details mean the actual average is slightly less. Set to 0 to disable modifiers altogether.
MODIFIER_CHANCE = 3
# Maximum number of rounds a player may go without submitting a word before they are considered idle.
MAX_IDLE_ROUNDS = 4
# Points to award per streak level beyond 1. Set to 0 to disable. (Someone on a streak of N thus receives a bonus of (N-1)*STREAK_BONUS.)
STREAK_BONUS = 4
# Number of seconds to wait between rounds.
NEW_TIME = 10
# Enable or disable dynamic hints for rounds which always have a single or very few possible answers (e.g. anag, def).
DYNAMIC_HINTS = True
# List of round formats that should not be loaded.
EXCLUDE_ROUNDS = ["exclude"]
# List of modifiers that should not be loaded.
EXCLUDE_MODIFIERS = []

# Symbol(s) prefacing all commands (see below).
COMMAND_PREFIX = "!"
# Specific names of various commands.
START_COMMAND = "whstart"
STOP_COMMAND = "whstop"

# Self-explanatory IRC-specific settings. KEY should be the empty string if the channel has none.
SERVER, PORT = 'chat.freenode.net', 6667
CHANNEL, KEY = '##logophiles', ''
NICK = 'Logophile'
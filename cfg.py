# Length of time each round lasts, in seconds.
ROUND_TIME = 50
# If the first answer submitted is over RESET_TIME seconds, reset the timer to this value.
RESET_TIME = 30
# Number of seconds to wait between rounds.
NEW_TIME = 10
# Symbol prefacing all commands (e.g. whstart, whstop).
COMMAND_PREFIX = "!"
# List of round formats that should not be loaded.
EXCLUDE_ROUNDS = ["exclude"]

# Self-explanatory IRC-specific settings. Enter a blank string for KEY if the channel has none.
SERVER, PORT = 'chat.freenode.net', 6667
CHANNEL, KEY = '##logophiles', ''
NICK = 'Logophile'
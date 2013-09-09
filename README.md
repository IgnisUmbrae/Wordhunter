Wordhunter
==========

About
-----

Wordhunter is an IRC bot that hosts a fiercely competitive and Ruinously Addictive™ word game based on the idea of 'hunting' the best words that fit certain criteria. Each word is worth its score in Scrabble plus its length, and it falls to you and your fellow competitors to find the best of the bunch. Here are some sample challenges, with round and modifier names in parentheses (mouse over the links for example solutions):

- Words that contain ICE but exclude A and T (blockend+exclude) ⇒ [Possible solution](# "POLICEWOMEN for 31")
- Subanagrams of IEGSTTPETMNN whose third and fourth letters are the same (subanag+same) ⇒ [Possible solution](# "PETTINGS for 19")
- Words that can be built using the letters E, R, H, O and S any number of times (onlyhas) ⇒ [Possible solution](# "HORSESHOES for 26")
- Words that begin with DIS and include F (blockstart+include) ⇒ [Possible solution](# "DISGRACEFULLY for 36")
- Words that begin with A and end with US in which every letter is unique (blockbeginend+unique) ⇒ [Possible solution](# "AMBIDEXTROUS for 43")

Support is available in [#Wordhunter on freenode](http://webchat.freenode.net/?channels=#Wordhunter), where I'm known as etotheipi.

Features
--------

- Stunning two-tier gameplay! In the struggle for points and ultimate lexical supremacy, will you turn to length or to letter rarity?
- Stunning educational value! Unless you manage the top-scorer, Wordhunter suggests the next best word for you, complete with definition!*
- Stunning default bank of nine round formats and four modifiers with easy extensibility!
- **Soon**: Stunning running commentary of multiplayer games!

*Most of the time, at least. Some words aren't defined yet.

Requirements
------------

- Python 2.7.x;
- [irclib](http://python-irclib.sourceforge.net/) 8.3+;
- Desirable but not essential: mad vocabulary skills.

Basic usage
-----------

Once you have your hands on the code, it's time to edit `cfg.py`. IRC-specific settings are nestled away at the bottom; all others pertain to the game itself. When you're done tinkering, run `bot.py` to begin.

At present, Wordhunter has but two commands, all elements of which are configurable: the defaults are `!whstart n=# t=#`, to start a game, and `!whstop`, to end it early. The optional parameters `n` and `t` respectively specify the number of rounds to play and the number of seconds each round lasts, may appear in any order and override the defaults in `cfg.py` if provided. So if you'd like to play a 20-round game with 30 seconds per round, you could issue the command `!whstart n=20 t=30`.

Writing extensions
------------------

Soon!

Future features
---------------

- Completed Future Features section

Acknowledgements
----------------

I am much indebted to the inestimable **contingo**, not only for his many ideas and constant suggestions for improvement, but also for our many five-minute-cum-five-hour test sessions that have brought rafts of bugs to my attention. Long may they continue.

Contributions
-------------

Until such time as the guide to writing extensions is complete, if you have a brilliant idea for a round format or modifier or any other such thing that you just can't contain, seek me out on freenode or submit a feature request and I'll see what I can do.

If for some reason you still have time to earn money with the bot in your midst and you'd like to donate, you can do so on [Pledgie](http://pledgie.com/campaigns/21862) or [Gittip](https://www.gittip.com/IgnisUmbrae). Anything and everything is greatly appreciated — Wordhunter is a labour of love, but it isn't half a time-hungry one. Thanks!
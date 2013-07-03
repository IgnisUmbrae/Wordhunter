import re

nesses = re.compile("^.+?NESS(ES)?$")
f = open('CSW12mw-wh.txt','r')
words = map(lambda x: x.strip(), f.readlines())
f.close()
f = open('blah.txt','w')
for w in words:
	if not nesses.match(w):
		f.write(w+'\n')
f.close()
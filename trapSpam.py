# -*- python -*-
import sys
import re
import time

msg = sys.stdin.read()
phrases = ("The entire body of the message was removed", 
		"--AOL Postmaster", 
		"l0ad",
		"eBay Store"
		)

open("/home/ed/trapspam.log", "a").write("%s: MESSAGE LENGTH: %s\n" % (time.ctime(), len(msg)))
try:
	mtch = re.search("(Subject: .+)").groups()[0]
	open("/home/ed/trapspam.log", "a").write("\t%s\n\n" % mtch)
except:
	pass

for phrase in phrases:
	if phrase in msg:
		pat = "Date: (.+)"
		repl = "Date: \g<1>\nX-Suspect-Mail: yes"
		msg = re.sub(pat, repl, msg)
		break
		
print msg

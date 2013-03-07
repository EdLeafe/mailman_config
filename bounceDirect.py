import getMsg
import time
import smtplib

msg = getMsg.getMsg()
fwdKey = "X-Forwarded-By: OT filtering script"
okHdr1 = "X-Original-To: profoxxtproxy@leafe.com"
okHdr2 = "X-Original-To: profox@leafe.com"
bounceHdr = "X-Forwarded-By: DIRECT POST"
emptyHdr = "X-EMPTY-MESSAGE: True"
ret = msg

#ff = open("/var/dummyLogs/BD.LOG", "a")
#ff.write("%s - %s (len=%s)\n" % (time.ctime(), msg.find(fwdKey), len(msg)))
problem = False
try:
	if len(msg) == 0:
#		ff.write("EMPTY MESSAGE - EXITING\n")
		ret = emptyHdr + "\n"
		problem = True
#	ff.write("msg.find(fwdKey): %s - " % msg.find(fwdKey))
	ok = (okHdr1 in msg) ###and (okHdr2 in msg)
	if not ok:
		# This is a direct post! Add the filter header
		pos = msg.find("From: ")
#		ff.write("POS: %s\n------msg-----------\n" % pos)
#		ff.write("\n%s\n---------end---------\n\n" % msg)
		ret = msg[:pos-1] + "\n" + bounceHdr + "\n" + msg[pos:]
		problem = True
#	if not problem:
#		ff.write("\n------msg-----------\n")
#		ff.write("\n%s\n---------end---------\n" % msg)
#		ff.write("No problems found.\n")
except StandardError, e:
	server = smtplib.SMTP("leafe.com")
	server.sendmail("BounceDirect@leafe.com", "ed@leafe.com", 
			"To: Ed Leafe <ed@leafe.com>\nSubject: Bounce Direct problem\n\nError encountered: %s\n\n%s" % (str(e), msg) )
	server.quit()

print ret

#ff.close()

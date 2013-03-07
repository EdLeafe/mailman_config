from Mailman import mm_cfg
from Mailman import Errors
from Mailman.Handlers import Hold
from Mailman.Logging.Syslog import syslog 
from Mailman.MailList import MailList
import os
from subprocess import Popen, PIPE
import re
import time

class ProFoxNonSubHold(Errors.HoldMessage):
	""" Non-subscriber to either list posting """
	reason = "Message from non-subscriber"
	rejection = "You are not a subscriber to ProFox or ProFoxTech"
	
	
def process(mlist, msg, msgdata):
	pfLists = ("profox", "profoxtech")
	listname = mlist.real_name
	tm = time.strftime("%Y.%m.%d %H:%M:%S",time.localtime())
	
	if listname.lower() in ("profox", "profoxtech"):
		if "X-Suspect-Mail: yes" in msg:
			# already flagged
			return
		snd = msg.get_sender()
		if snd == "discardme@leafe.com":
			# It'll get discarded anyway
			return
		
		logMsgs = []
		logMsgs.append("%s-> List: %s, Sender: %s" % (tm, listname, msg.get_sender()))
		cmd = "/usr/local/mailman/bin/find_member %s" % snd
		proc = Popen([cmd], shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
		f, stdin = (proc.stdout, proc.stdin)
		res = f.read().replace(" ", "").splitlines()
		res = res[1:]
		logMsgs.append("Findmember LISTS: %s" % str(res))
		ok = (pfLists[0] in res) or (pfLists[1] in res)
		logMsgs.append("\tOK LIST: %s" % ok)
		if not ok:
			ok = snd in mlist.accept_these_nonmembers
			logMsgs.append("\tOK ACCEPT: %s" % ok)
		if not ok:
			# Check the other list
			otherNameList = ["profox", "profoxtech"]
			otherNameList.remove(mlist.internal_name())
			otherName = otherNameList[0]
			otherList = MailList(otherName)
			ok = snd in otherList.accept_these_nonmembers
			logMsgs.append("\tOK OTHER ACCEPT: %s" % ok)
			otherList.Unlock()
		if not ok:
			logMsgs.append("\tNot a subscriber: %s" % snd)
			syslog("vette", "%s post from %s held: non-subscriber to either ProFox list. " % (listname, snd))
			#syslog("vette", str(res))
			try:
				Hold.hold_for_approval(mlist, msg, msgdata, ProFoxNonSubHold(snd))
			except StandardError, e:
				logMsgs.append("ERROR: %s" % str(e))
				
		if not ok:
			open("/usr/local/mailman/profox.log", "a").write("\n".join(logMsgs))
	return


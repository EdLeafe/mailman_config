# -*- python -*-
import sys

def getMsg():
        lcRetVal = ""
        while 1:
                ch = sys.stdin.read(1)
                lcRetVal = lcRetVal + ch
                if ch == "": break
        return lcRetVal

lcOut = ""

lcDashLine = "_"  * 40
lcMaintLine1 = "Post Messages to: "
lcMaintLine2 = "Subscription Maintenance: "
# ProFox
lcMaintLine1PF = "Post Messages to: ProFox@leafe.com"
lcMaintLine2PF = "Subscription Maintenance: http://leafe.com/mailman/listinfo/profox"
# ProLinux
lcMaintLine1PL = "Post Messages to: ProLinux@leafe.com"
lcMaintLine2PL = "Subscription Maintenance: http://leafe.com/mailman/listinfo/prolinux"
lcStripMsg = "[excessive quoting removed by server]"

lcMsg = getMsg()
laMsg = lcMsg.splitlines(1)   # keep the newlines

# track the status. Use the following codes
# 0 = Nothing noted yet
# 1 = dashed line found
# 2 = first maint line found
lcStatus = 0
# In case we get a false initial detection, create a holding area
lcHold = ""

for lcLine in laMsg:
	if lcLine.find(lcStripMsg) > -1:
		# They've 	quoted the strip message: LOSERS! Kill it here.
		lcOut += lcStripMsg + "\n"
		break

	if lcStatus == 0:
		# See if we are have found a dashed line. If not, add it to the output
		if lcLine.find(lcDashLine) > -1:
			lcStatus = 1
			lcHold += lcLine
		else:
			lcOut += lcLine
	
	elif lcStatus == 1:
		# We have already found a dash line. See if the first sub line is found
		#if (lcLine.find(lcMaintLine1PF) > -1) or lcLine.find(lcMaintLine1PL) > -1:
		if (lcLine.find(lcMaintLine1) > -1):
			lcStatus = 2
			lcHold += lcLine
		else:
			# False alarm. Add the held content, and the current line to output
			lcStatus = 0
			lcOut += lcHold + lcLine
			lcHold = ""

	elif lcStatus == 2:
		# OK, this is the test. If we find the second sub line, scrap everything afterwards
		#if (lcLine.find(lcMaintLine2PF) > -1) or lcLine.find(lcMaintLine2PL) > -1:
		if (lcLine.find(lcMaintLine2) > -1):
			lcOut += lcStripMsg + "\n"
			break
		else:
			# False alarm. Add the held content, and the current line to output
			lcStatus = 0
			lcOut += lcHold + lcLine
			lcHold = ""

print lcOut

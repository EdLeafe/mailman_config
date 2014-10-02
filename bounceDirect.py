import email
import getMsg
import re
import smtplib
import time

msg = getMsg.getMsg()

fwdKey = "X-Forwarded-By: OT filtering script"
okHdr1 = "X-Original-To: profoxxtproxynn7@leafe.com"
okHdr2 = "X-Original-To: profox@leafe.com"
bounceHdr = "X-Forwarded-By: DIRECT POST"
emptyHdr = "X-EMPTY-MESSAGE: True"
ret = msg

def logit(*args):
    txt = " ".join(["%s" % arg for arg in args])
    with open("/var/dummylogs/BD.LOG", "a") as ff:
        ff.write("%s\n" % txt)

logit("%s - %s (len=%s)\n" % (time.ctime(), msg.find(fwdKey), len(msg)))
problem = False

try:
    if not msg:
        logit("EMPTY MESSAGE - EXITING\n")
        ret = emptyHdr + "\n"
        problem = True
    logit("msg.find(fwdKey): %s - " % msg.find(fwdKey))
    ok = (okHdr1 in msg) ###and (okHdr2 in msg)
    if not ok:
        # This is a direct post! Add the filter header
        eml = email.message_from_string(msg)
        del eml["X-Forwarded-By"]
        del eml["X-Forwarded-By"]
        eml["X-Forwarded-By"] = "DIRECT POST"
        ret = eml.as_string()
        problem = True
    if not problem:
        logit("\n------msg-----------\n")
        logit("\n%s\n---------end---------\n" % msg)
        logit("No problems found.\n")
except StandardError, e:
    server = smtplib.SMTP("leafe.com")
    server.sendmail("BounceDirect@leafe.com", "ed@leafe.com", 
            "To: Ed Leafe <ed@leafe.com>\nSubject: Bounce Direct problem\n\nError encountered: %s\n\n%s" % (str(e), msg) )
    server.quit()

print ret

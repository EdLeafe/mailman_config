#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import email
from email.header import decode_header
import logging
import os
from subprocess import Popen, PIPE
import sys
import time
import traceback
import MySQLdb

msg_text = ""
logger = logging.getLogger("archive")
handler = logging.FileHandler("/var/dummylogs/arch.debug")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.formatter = formatter
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def getMsg():
    ret = []
    while True:
        chars = sys.stdin.read(1024)
        ret.append(chars)
        if not(chars):
            break
    return "".join(ret)


def logit(*args):
    msg = " ".join(["%s" % arg for arg in args])
    logger.info(msg)


def headerToUnicode(eml, hdr):
    decHdr = decode_header(eml[hdr])
    ret = " ".join([val for val, enc in decHdr])
    encds = [enc for val, enc in decHdr
            if enc is not None]
    if encds:
        ret = unicode(ret, encds[0])
    return ret


def stripBody(contents):
    if not contents:
        return ""
    elif isinstance(contents, basestring):
        return contents.strip()
    elif isinstance(contents, list):
        c0 = contents[0]
        if isinstance(c0, email.message.Message):
            return c0.as_string().strip()
        else:
            return c0.strip()
    return ""


def addToArchive(listName, crs=None, fromScript=0):
    global marker, msg_text
    logit("Getting message...")
    msg_text = getMsg()
    msg = email.message_from_string(msg_text)
    logit("LENTXT: ", len(msg_text))
#    logit("TXT:", msg)

    marker = "initial"
    # Handle exceptions to the 'initial' rule
    try:
        listAbbrev = {"prolinux": "l", "propython": "y", "dabo-users": "u"}[listName]
    except KeyError:
        listAbbrev = listName[0]
    tt = email.utils.parsedate_tz(msg["Date"])
    utc = email.utils.mktime_tz(tt)
    dt = datetime.datetime.fromtimestamp(utc)
    marker = "payload body"
    body = msg.get_payload()
    marker = "payload dbody"
    dbody = msg.get_payload(decode=True)
    enc = msg.get_content_charset()
    logit("CONTENT CHARSET:", enc)
    if enc:
        dbody = dbody.decode(enc)

    try:
        dbody = dbody.encode("utf8")
    except StandardError, e:
        logit("Can't encode: %s; %s\n" % (type(e), e))

    body = stripBody(body)
    dbody = stripBody(dbody)
    logit("LENBODY:", len(body), "LENDBOD:", len(dbody))

#if body != dbody:
#    file("/var/dummylogs/dbody", "a").write("%s\n\n\n" % dbody)

    msgID = msg["Message-ID"].lstrip("<").rstrip(">")
    replyToID = msg.get("In-Reply-To", "").lstrip("<").rstrip(">")
    marker = "FROM"
    fromAddr = headerToUnicode(msg, "From")
    marker = "SUBJ"
    subj = headerToUnicode(msg, "Subject")
    # Eliminate any password reminder emails
    if "mailing list memberships reminder" in subj:
        return

    createCursor = (crs is None)
    for host in ("cloud-webdata", "leafe.com"):
        if createCursor:
            try:
                db=MySQLdb.connect(host=host, user="mysql",
                    passwd="fil0farn", db="webdata", charset="utf8")
                crs = db.cursor()
            except Exception:
                logit("DB Connection failed to", host)
                continue

        logit("Connecting with host:", host)
        marker = "before insert"
        logit("LEN INSERT:", len(dbody))
        crs.execute("""insert into archive (clist, csubject, cfrom, tposted,
            cmessageid, creplytoid, mtext)
            values (%s, %s, %s, %s, %s, %s, %s)""",
            (listAbbrev, subj, fromAddr, dt, msgID, replyToID, dbody))

        try:
#            crs.execute("select max(imsg) from archive")
#            id_ = crs.fetchone()[0]
            crs.execute("select LAST_INSERT_ID() from archive")
            id_ = crs.fetchone()[0]
            logit("  ID:", id_)
            crs.execute("select cfrom, length(mtext) from archive where imsg = %s", (id_, ))
            frm, txtlen = crs.fetchone()
            logit("FROM:", frm.encode("utf8"))
            logit("  TXT DIFF:", (len(dbody) - txtlen))
        except StandardError, e:
            logit("Could not get ID:", e)

        if createCursor:
            # If we opened it, let's close it.
            try:
                crs.close()
                db.close()
                logit("Disconnecting from host:", host)
            except:
                pass
    return True


#BEGIN PROCEDURE
if __name__ == "__main__":

#    import inspect
#    stack = inspect.stack()
#    logit("-" * 33)
#    for level in stack[::-1]:
#        logit(level[0])
#    logit("-" * 33)

    try:
        arg0 = "just entering"
        marker = "just entering"
        arg0 = sys.argv[0]
        listName = sys.argv[1].lower()

        logit("List Name", listName)
        if not listName in ("profoxtech", ):
            marker = "before call to addToArchive"
            logit("Calling 'addToArchive'")
            addToArchive(listName)

    except StandardError as e:
        with open("/var/dummylogs/arch.error", "a") as f:
            f.write("\n\n")
            f.write("-" * 88)
            f.write("\n")
            f.write("Arg0 = %s\n" % arg0)
            f.write("marker = %s\n" % marker)
            ltime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            tb = traceback.format_exc()
            f.write("\n%s\n------\n%s\n" % (ltime, tb))
            f.write("---------\nSOURCE:\n")
            f.write("%s\n" % msg_text)
            f.write("-" * 88)
            f.write("\n")

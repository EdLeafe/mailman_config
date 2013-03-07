#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import email
from email.header import decode_header
import os
from subprocess import Popen, PIPE
import sys
import time
import traceback
import MySQLdb

msg_text = ""


def getMsg():
	ret = []
	while True:
		chars = sys.stdin.read(1024)
		ret.append(chars)
		if not(chars):
			break
	return "".join(ret)


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
		return contents[0].strip()
	return ""


def addToArchive(listName, crs=None, fromScript=0):
	global marker, msg_text
	msg_text = getMsg()
	msg = email.message_from_string(msg_text)
#	file("/var/dummylogs/arch.msg", "a").write("LENTXT: %s\nTXT: %s\n" % 
#			(len(msg_text), msg))

	marker = "initial"
#	 Handle exceptions to the 'initial' rule
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
#	file("/var/dummylogs/arch.msg", "a").write("CONTENT CHARSET: %s\n" % enc)
	if enc:
		dbody = dbody.decode(enc)

	try:
		dbody = dbody.encode("utf8")
	except StandardError, e:
		file("/var/dummylogs/arch.debug", "a").write("Can't encode: %s; %s\n" %
				(type(e), e))
		
#	file("/var/dummylogs/arch.msg", "a").write("LENBODY: %s\nLENDBOD: %s\n\n" % 
#			(len(body), len(dbody)))
	body = stripBody(body)
	dbody = stripBody(dbody)

#if body != dbody:
#	file("/var/dummylogs/dbody", "a").write("%s\n\n\n" % dbody)
		
	msgID = msg["Message-ID"].lstrip("<").rstrip(">")
	replyToID = msg.get("In-Reply-To", "").lstrip("<").rstrip(">")
	marker = "FROM"
	fromAddr = headerToUnicode(msg, "From")
	marker = "SUBJ"
	subj = headerToUnicode(msg, "Subject")
#	 Eliminate any password reminder emails
	if "mailing list memberships reminder" in subj:
		return
		
	createCursor = (crs is None)
	for host in ("cloud-webdata", "leafe.com"):
		if createCursor:
			db=MySQLdb.connect(host=host, user="mysql", 
				passwd="fil0farn", db="webdata", charset="utf8")
			crs = db.cursor()

#		file("/var/dummylogs/arch.debug", "a").write("Connecting with host: %s\n" % host)
		marker = "before insert"
#		file("/var/dummylogs/arch.debug", "a").write("LEN INSERT %s\n" % len(dbody))
		crs.execute("""insert into archive (clist, csubject, cfrom, tposted, 
			cmessageid, creplytoid, mtext)
			values (%s, %s, %s, %s, %s, %s, %s)""", 
			(listAbbrev, subj, fromAddr, dt, msgID, replyToID, dbody))

		try:
#			crs.execute("select max(imsg) from archive")
#			id_ = crs.fetchone()[0]
			crs.execute("select LAST_INSERT_ID() from archive")
			id_ = crs.fetchone()[0]
#			file("/var/dummylogs/arch.debug", "a").write("  ID: %s " % (id_, ))
			crs.execute("select cfrom, length(mtext) from archive where imsg = %s", (id_, ))
			frm, txtlen = crs.fetchone()
#			file("/var/dummylogs/arch.debug", "a").write("FROM: %s\n" % frm.encode("utf8"))
#			file("/var/dummylogs/arch.debug", "a").write("  TXT DIFF: %s\n" % (len(dbody) - txtlen))
		except StandardError, e:
			file("/var/dummylogs/arch.debug", "a").write("Could not get ID: %s\n" % e)
			
		if createCursor:
			# If we opened it, let's close it.
			try:
				crs.close()
				db.close()
				file("/var/dummylogs/arch.debug", "a").write("Disconnecting from host: %s\n" % host)
			except:
				pass
	return True


#BEGIN PROCEDURE
if __name__ == "__main__":
	try:
		arg0 = "just entering"
		marker = "just entering"
		arg0 = sys.argv[0]
		listName = sys.argv[1].lower()

		if not listName in ("profoxtech", ):
			marker = "before call to addtoarchive"
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

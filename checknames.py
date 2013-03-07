
from Mailman.MailList import MailList

ml = MailList("profoxtech")
members = ml.members.keys()
print "#NUM:", len(members)
notInPF = []

for addr in file("pfnames.txt"):
	addr = addr.strip()
	if addr in members:
		print "cool:", addr
		continue
	notInPF.append(addr)

file("notInPFT.txt", "w").write("\n".join(notInPF))

ml.Unlock()


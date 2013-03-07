import sys

def getMsg():
	lcRetVal = ""
	while 1:
				ch = sys.stdin.read(1)
				lcRetVal = lcRetVal + ch
				if ch == "": break

	return lcRetVal

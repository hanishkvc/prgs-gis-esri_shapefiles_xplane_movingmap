#!/usr/bin/env python3
#
# Helper routines for Debug
# HanishKVC, 2014
# GPL
#

# Debug Level 0

import sys

DBGLVL_CRITICAL=0
DBGLVL_GENERAL=1
DBGLVL_MISC=2
DBGLVL_VLOW=3

DBGLVL_CURRENT=DBGLVL_CRITICAL

def dprint(dbgLvl, sMsg):
	if (dbgLvl <= DBGLVL_CURRENT):
		print(sMsg)

def dREP(sMsg, aGlobals=globals(), aLocals=locals()):
	bContinue = True
	print("Entering Exec Mode")
	print(sMsg)
	while bContinue:
		try:
			res=exec(input("?:"),aGlobals,aLocals)
			if (res != None):
				print(res)
		except KeyboardInterrupt:
			print("Exiting Exec loop")
			break
		except SystemExit:
			print("Quiting App...")
			break
		except:
			print(sys.exc_info())

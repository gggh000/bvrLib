from api import *
import re
import time

#   userProfile.py - user profile implements all aspect of user profile object in this platform.
#   Having multiple users allows it to create multiple independent mining operation in respect to
#   miner and coin. In short, the user A can define their user profile and miner profile and start
#   mining coin-A and using miner-A software completely independent from user B who has defined 
#   his own miner and user profile and chose to mine using miner-B software to mine coin-B.

#   =================================================================================================
#   Define constant, variables, path, directories, static definitions and initialization section.
#   =================================================================================================

class uProfile:
    userWallet = {}
    userInitials = None

    def __init__(self):
        dummy =  0
        return None

    def dummy(self):
        dummy = 0
        return None

def constructUserProfile(pInitials):
    CONFIG_PATH_MINER_USER_CFG = MINING_PLATFORM_ROOT + "/scripts/userProfile.cfg"
    entryFound = None
    entryEnd = None
    line = 1
    debugL2 = 0
    debug = 1
    dict1 = {}

    if not pInitials:
        printDbg("ERR: pInitials are empty.")
        return EXIT_ERR
    else:
        printDbg("pInitials: " + str(pInitials))

    fp = open(CONFIG_PATH_MINER_USER_CFG, 'r')

    if not fp:
        printDbg("ERR: Can not open " + str(CONFIG_PATH_MINER_USER_CFG))
        return EXIT_ERR

    # Read line by line and construct it.

    while line:
        line = fp.readline()

        printDbg("line: " + str(line), None, None, debugL2)

        if entryFound == 1 and re.search("ENTRY", line):
            entryEnd = 1
            printDbg("End of entry")
            break

        if re.search("ENTRY=" + str(pInitials), line):
            printDbg("Entry found...", None, None, debug)
            entryFound = 1
            dict1["username"] = pInitials
            continue

        if entryFound == 1 and entryEnd != 1:
            if not re.search(':', line):
                printDbg("WARN: invalid line: " + str(line), None, None, debugL2)
                continue

            currKey = line.split(':')[0].strip()
            currVal = line.split(':')[1].strip()

            printDbg("currKey/curValue: " + str(currKey) + ", " + str(currVal), None, None, debugL2)
            dict1[currKey] = currVal

    if entryFound:
        if debug:
            printDbg("constructUserProfile(): Returning constructed dictionary userProfile object for : " + str(pInitials))
            print dict1
    else:
        printDbg("ERR: Unable to find the entry: " + str(pInitials))
        return EXIT_ERR
    return dict1


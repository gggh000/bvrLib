from api import *
import re
import time

#   powerProfile.py: implements all aspects of power profile. This platform can support multiple
#   user profile to which powerProfile object is tied. Doing so allows different users define their
#   power profile differently allowing independently choose their power settings. There is only one 
#   way to associate power profile to a specific user however it can be worked around by defining 
#   two user profile for single user and associating a powerProfile to each user, there by creating
#   effect of two different power profiles. This way,a  user can section their miners into different 
#   power profile characteristics based on geographical location (due to weather etc), or some 
#   other classification system.

#   =================================================================================================
#   Define constant, variables, path, directories, static definitions and initialization section.
#   =================================================================================================

#   =================================================================================================
#   Start of API, function and class definitions.
#   =================================================================================================
    
#   Reads over powerProfile.cfg where the miner profile properties are defined.
#   input:
#   - pEntry - entry name. "miner-coin-pool" pre-defined combined  string.
#   output:
#   - EXIT_ERR - on any error condition.
#   - powerProfile object upon successful construct.

def constructPowerProfile(pEntry):
    CONFIG_PATH_POWER_PROFILE_CFG = MINING_PLATFORM_ROOT + "/scripts/powerProfile.cfg"
    entryFound = None
    entryEnd = None
    globalFound = None
    globalEnd = None

    line = 1
    debugL2 = 0
    debug = 1
    dict1 = {}

    fp = open(CONFIG_PATH_POWER_PROFILE_CFG, 'r')

    if not fp:
        printDbg("ERR: Can not open " + str(CONFIG_PATH_POWER_PROFILE_CFG))
        return EXIT_ERR

    # Read line by line and construct it.

    while line:
        line = fp.readline()

        printDbg("line: " + str(line), None, None, debugL2)

        if re.search("^#", line):
            printDbg("skipping commented line" + str(line), None, None, debugL2)
            continue

        if entryFound == 1 and re.search("ENTRY", line):
            entryEnd = 1
            printDbg("End of entry")
            break

        if globalFound == 1 and re.search("ENTRY", line):
            globalEnd = 1
            globalFound = None
            printDbg("End of global section")
            continue

        if re.search("GLOBAL", line):
            printDbg("Global section start")
            globalFound = 1
            continue

        if re.search("ENTRY=" + pEntry, line):
            printDbg("Entry found: " + str(line), None, None, debug)
            entryFound = 1
            globalFound = None
            continue

        if entryFound == 1 and entryEnd != 1:
            if not re.search(':', line):
                printDbg("WARN: invalid line: " + str(line), None, None, debug)
                continue

            currKey = line.split(':')[0].strip()
            currVal = line.split(':')[1].strip()

            printDbg("currKey/curValue: " + str(currKey) + ", " + str(currVal), None, None, debug)
            dict1[currKey] = currVal

        if globalFound == 1 and globalEnd != 1:
            if not re.search(':', line):
                printDbg("WARN: invalid line: " + str(line), None, None, debug)
                continue

            currKey = line.split(':')[0].strip()
            currVal = line.split(':')[1].strip()

            printDbg("currKey/curValue: " + str(currKey) + ", " + str(currVal), None, None, debug)
            dict1[currKey] = currVal

    if debug:
        printDbg("constructPowerProfile(): Returning constructed dictionary powerProfile object for : " + str(pEntry))
        print dict1

    return dict1



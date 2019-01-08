import os

# API-s, routines and definitions to be used throughout the smart miner software architecture are all declared here.

# Power profile - all definitions related to power related operations are defined here. 
# Power profiles are assigned to MinerPool.

# Cron profile - names of the cron file to be effective when activated. The cron profile contains all scheduled activities
# group of miners can have. Cron profile are assigned to MinerPool.

# MinerPool - Group of miner pool that can consist of 1 or more all the way to all miners in the domain.
# Miner pool are assigned to only one user-profile.
# It might be possible to assign more than one miner pool to single user but not vice versa.

MINING_PLATFORM_ROOT="/git.co/cs.dev/mining"
NVIDIA_SMI_LOG=MINING_PLATFORM_ROOT + "/scripts/client/nvidia-smi.log"

#   API fucntion return definitions.

EXIT_ERR = 1

# BAR-s definitions.

BAR2 = "=============================================="
BAR1 = "----------------------------------------------"

PRINTDBG_PARAM_OVERWRITE = 1

#   Color class def

class colors:
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    LIBLUE = '\033[96m'
    WHITEBOLD = '\033[97m'
    ENDC = '\033[97m'
    LIGREEN = '\033[96m'
    PURPLE = '\033[95m'
    GRAY = '\033[90m'

#   Print string with no new line.
#   req:
#   - None
#   input:
#   - pString - string to print.
#   return:
#   - None

def printNnl(pString):

    if pString != None:
        sys.stdout.write(pString)
    else:
        sys.stdout.write(".None?.")

def printWarn(pStr):
    LINE_SIZE = 80
    printDbg(colors.WARNING + "================================================================================" + colors.ENDC)

    for i in range(0, len(pStr), LINE_SIZE):
        printDbg(colors.WARNING + str(pStr[i:i+LINE_SIZE]))

    printDbg(colors.WARNING + "================================================================================" + colors.ENDC)
    printDbg(colors.ENDC + "...")

#   print function to be used by python scripts. 
#   input:
#   - pStr - string to be printed.
#   - pLog - full path of log file to be output in addition to stdout.
#   - pOverwrite - if set to PRINTDBG_PARAM_OVERWRITE, then overwrite the file otherwise append.
#   - pDebug - pass on debug variable, if set to 1 will print, otherwise will not print.

#   return 
#   - None - no error
#   - EXIT_ERR for any error encountered.

def printDbg(pStr, pLog = None, pOverwrite = None, pDebug = 1):
    debug = 0

    if not pStr:
        print "ERROR: pStr is empty!"
        return EXIT_ERR

    if not pLog and debug:
        print "WARNING: pLog is empty, will not output to log: ", pStr
        return EXIT_ERR

    #   Unfortunately python fp pointer is not reliable, cutting the file on append write for no apparent
    #   reason, decided to call os.system() call to do the writing.

    if pLog:
        LOG_CMD="echo \"" + str(pStr) + "\" >> " + str(pLog)

        if debug:
            print "log output constructed: ", LOG_CMD

        if pOverwrite == PRINTDBG_PARAM_OVERWRITE:
            fpLog = open(pLog, 'w')
        else:
            fpLog = open(pLog, 'a')
    
        if not fpLog:
            print "ERROR: Failed to open file for writing: ", str(pLog)
    
        fpLog.write(pStr + '\n')
        stat=fpLog.close()
        
        if debug:
            print "fpLo.close stat: " + str(stat)

    if pDebug:
        print pStr

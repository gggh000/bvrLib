#!/usr/bin/python

#   start.mining.y - constructs all parameters required for mining to start including username, hostname
#   command structures, pool url, password and launches the miner software with constructed parameters.
#   This script is designed to be called from client/fast-check.py
#   however it can be started from command line directly by ./start.mining.py <miner-name>-<coin-name>.
#   For a list of supported miners and coin combinations, refer to minerCoinPoolAttribs or minersAvailable
#   dictionary keys or use ./start.mining.py --help. 

#   =================================================================================================
#   Define constant, variables, path, directories, static definitions and initialization section.
#   =================================================================================================

from socket import gethostname; 
import time 
import sys 
import os
import re
from userProfile import * 
from minerProfile import *
from api import *  
testMode = 0
currMinerProfile = None 
CURR_PID_FILE = MINING_PLATFORM_ROOT + "/log/currpid.log"
LOG_FILE_MINER = MINING_PLATFORM_ROOT + "/log/miner.log"
LOG_FILE_START_MINING_PY = MINING_PLATFORM_ROOT + "/log/start.mining.log"
MINER_START_ABORT = None
MINER_START_ABORT_REASON = "None."
debug = 0
minerProfileV2={}

#   Constants definitions.

CONFIG_DIR_LOG = MINING_PLATFORM_ROOT + "/log"
CONFIG_DIR_LOGGER = MINING_PLATFORM_ROOT + "/logger"
CONFIG_LOGGER_GPU_FNAME = "gpu-data-logger.sh"
CONFIG_LOGGER_BTG_DIFFICULTY_FNAME = "difficulty-logger-btg.sh"
CONFIG_LOGGER_ZEC_DIFFICULTY_FNAME = "difficulty-logger-zec.sh"
CONFIG_LOGGER_ZEN_DIFFICULTY_FNAME = "difficulty-logger-zen.sh"
CONFIG_LOGGER_ZCL_DIFFICULTY_FNAME = "difficulty-logger-zcl.sh"
CONFIG_LOGGER_ETC_DIFFICULTY_FNAME = "difficulty-logger-etc.sh"

LOGGER_BATCH = [CONFIG_LOGGER_GPU_FNAME, CONFIG_LOGGER_ZEC_DIFFICULTY_FNAME]
MINER_START_ABORT = 0

#   Variables definitions.

minerToRun=None

#   Password to be sent to pool by default.

PASSWORD = 94538

#   Default cuda devices range before determining dynamically. 

CUDA_DEVICES_RANGE = "0 1 2 3"

os.system("touch " + str(LOG_FILE_START_MINING_PY))
printDbg(BAR2, LOG_FILE_START_MINING_PY)
DATE=os.popen("date").read()
printDbg("Start.mining.py log started at " + str(DATE), LOG_FILE_START_MINING_PY)

#   Update cuda devices range based on gpu artifact left by fast-check.py. 
#   It file does not exist, use nvidia-smi to determine. THe count-gpus.sh will 
#   determine the number of GPU-s currently installed. For any error encountered 
#   in determining the number of GPU-s dynamically, use default range of 0-3.

try:
    GPUS=os.popen("cat " + str(MINING_PLATFORM_ROOT) + "/log/gpus.log").read()
    printDbg("No. of GPUs...: " + str(GPUS))

    if GPUS == None:
        printDbg("ERR: Unable to determine No. of GPUs!!! Determining using nvidia-smi.")
        os.system("./count-gpus.sh")
        GPUS=os.system("cat " + str(MINING_PLATFORM_ROOT) + "/log/gpus.log")
        printDbg("GPUS: " + str(GPUS))

    printDbg("No. of GPUs...: " + str(GPUS))

    CUDA_DEVICES_RANGE=""

    GPUS=int(GPUS)

    for i in range(0, GPUS):
        printDbg("Adding " + str(i) + " to cuda devices range.")
        CUDA_DEVICES_RANGE += str(i) + " "
    CUDA_DEVICES_RANGE = CUDA_DEVICES_RANGE.strip()

except Exception as msg:
    printDbg("Can not determine the exact No. of number of GPU-s, defaulting to 4.", LOG_FILE_START_MINING_PY)
    print msg
    CUDA_DEVICES_RANGE="0 1 2 3"

printDbg("CUDA devices range: " + str(CUDA_DEVICES_RANGE), LOG_FILE_START_MINING_PY)

#   CONFIG_GPU_MINER_POWER_INTENT_SUPPORT is how much power is miner 
#   set to default when starting the miner if not override or limit setting.
#   It is desired power at which the particular GPU operate.
#   if no CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT and/or CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT 
#    is set at particular miner, this is the power at which it will operate. 

if testMode:
    CONFIG_WAIT_INTERVAL = 5
else:
    CONFIG_WAIT_INTERVAL = 10

#   Dictionary list describing the each specific miner-coin-pool attributes. 
#   The value of the dictionary holds the list atrtibutes which is used when creating minerProfile instances.
#   minerProfile struct members are in turn used in constructing the ultimate command sent to miner.

HOSTNAME=gethostname()

#   Determine miner user profile to use set on this particular miner. If no miner is defined, use default user
#   profile.

try:
    MINER_PROFILE=os.environ['MINER_PROFILE']
except Exception as msg:
    printDbg("Warning: Unable to get the MINER_PROFILE O/S environment setting. \
        Setting to default miner profile: " + str("GG"), LOG_FILE_START_MINING_PY)
    MINER_PROFILE="GG"

if not MINER_PROFILE:
    printDbg("Error: miner profile name is not not set.", LOG_FILE_START_MINING_PY)
    quit(1)
else:
    printDbg("user profile name: " + str(MINER_PROFILE), LOG_FILE_START_MINING_PY)

#   Setup user profile instance. (This appears to be not used).

userCurrent = uProfile()

userCurrent={}
userCurrent=constructUserProfile(MINER_PROFILE)

if userCurrent == EXIT_ERR:
    printDbg("ERR: User does not appear to exist: " + str(MINER_PROFILE))
    quit(1)

for i in minersAvailable:
    printDbg(BAR2)
    printDbg("Constructing " + str(i))
    stat = constructMinerProfile(i)

    if stat != EXIT_ERR:
        minerProfileV2[i] = stat
        minerProfileV2[i]["cuda"]=CUDA_DEVICES_RANGE
        minerProfileV2[i]["hostname"] = HOSTNAME

        #   Determine if address needs to be set.

        # Determine the coin. Then find the key from userProfile and fetch the corresponding address.
        # Set it to user field.

        coin=minerProfileV2[i]["coin"]

        if not coin in userCurrent.keys():
            printDbg("WARN: User profile: " + str(userCurrent["username"]) + " has no address for " + str(coin))
        else:
            minerProfileV2[i]["address"] = userCurrent[coin]

        minerProfileV2[i]["minerCmd"] = constructMinerCmd(minerProfileV2[i])
    else:
        printDbg("Did not find a profile definition for " + str(i) + " in minerProfile.cfg")
    time.sleep(0)

printDbg("Finished constructing minerProfile V2")

for i in minerProfileV2.keys():
    printDbg("--------------")
    printDbg("key: " + str(i))
    #print minerProfileV2[i]

time.sleep(3)

#   User profile index holds the index of user currently set on this miner within the user list.
#   This index is used to index into each coin's wallet address lists and construct userWallet object.
#   User wallet object will hold the particular user (current user)'s all coin addresses.

#   =================================================================================================
#   Start of execution section.
#   =================================================================================================

os.system("clear")

printDbg("Hostname: " + str(HOSTNAME), LOG_FILE_START_MINING_PY)

#   This appears to be useless code, delete after a while.

#   !!!! This is error after removing the obsolete path definitions which now defined in minerProfile.cfg.
#printDbg("Miners defined: " + str(CONFIG_LOC_MINER_LIN_EWBF_ZEC), LOG_FILE_START_MINING_PY)

#   sys.argv[1] holds the miner-coin combination or miner-coin-pool combination. In case
#   of miner-coin combination with pool specified, default miner-coin-pool combination assigned 
#   to miner-coin is used.

try:
    minerToRun=sys.argv[1]
except Exception as msg:
    printDbg("Error: You need to input miner...", LOG_FILE_START_MINING_PY)
    printDbg("Availeble miners: ", LOG_FILE_START_MINING_PY)
    print minersAvailable
    quit()

printDbg("Miner to run: " + str(minerToRun), LOG_FILE_START_MINING_PY)

if minerToRun not in minersAvailable:
    if minerToRun not in minersDefault:
        printDbg("This miner is not available: " + str(minerToRun), LOG_FILE_START_MINING_PY)
        printDbg("Availeble miners: ", LOG_FILE_START_MINING_PY)
        print minersAvailable
        quit(1)
    else:
        minerToRun=minersDefault[minerToRun]

printDbg("Miner to run /default/: " + str(minerToRun), LOG_FILE_START_MINING_PY)
time.sleep(3)

#   Only start the miner when no other processes are using it. If nvidia-smi output does not display
#   "no running process found" message, set abort flag, which in turn will not launch another instances 
#   of the miner anew.

#   !!!! Consider using nvidia_smi_log!!!!

stat = os.popen("nvidia-smi | egrep \"No running processes found\"" ).read() 

if not re.search("No running processes found", str(stat)):
    printDbg("Another miner or process might be using GPU. Miner launch will be aborting...", LOG_FILE_START_MINING_PY)
    print str(stat)
    MINER_START_ABORT=1
    MINER_START_ABORT_REASON="Another miner or process might be using GPU. Miner launch will be aborting..."

os.system(str(MINING_PLATFORM_ROOT) + "/scripts/set-power.py")
time.sleep(CONFIG_WAIT_INTERVAL)

printDbg("Checking if any miner is running:", LOG_FILE_START_MINING_PY)

'''
#   !!!! Consider using nvidia_smi_log!!!!
#   !!!! This code appears to be totally messed up, fix it soon!!!!

stat = os.popen("nvidia-smi | egrep \"" +  minerProfileV2[minerToRun]["miner"] +"\"" ).read() 

if re.search("CONFIG_FNAME_MINER_LIN_EWBF_BTG", str(stat)):
	printDbg("Another miner is already running. Aborting...", LOG_FILE_START_MINING_PY)
	print str(stat)
	exit(1)
'''

printDbg("OK, starting the miner..." + str(minerToRun), LOG_FILE_START_MINING_PY)

#   Construct miner commands, using currMinerProfile data object created earlier.
try:
    printDbg("minerProfile selected: ")
    print minerProfileV2[minerToRun]
    time.sleep(3)
except Exception as msg:
    printWarn("ERROR: This miner-coin-pool combination is not defined in minerProfile.cfg file: " + str(minerToRun))
    printWarn("Please add definition before running. Currently defined combinations: ")
    print minerProfileV2.keys()
    quit(1)

if not minerProfileV2[minerToRun]["minerCmd"]:
    printDbg("ERR: minerCmd appears empty.")
    quit(1)

try:
    minerCmd1 = minerProfileV2[minerToRun]["minerCmd"]
except Exception as msg:
    printDbg("Error: current miner/coin: " + str(minerToRun) + " is not supported or need to be added.", LOG_FILE_START_MINING_PY)
    print msg
    quit(1)

#   Perform more validation for minerCmd.

    if minerCmd1 == EXIT_ERR or minerCmd1 == None:
        printDbg("Error: minerCmd constructed was NONE or EXIT_ERR: " + str(minerCmd1) + ". This means some error happened during processing of minerProfile.cfg")
        quit(1)

if re.search("<.*>", minerCmd1):
    printDbg("Error: minerCmd contains unprocessed placeholder value in triangle brackets: " + str(minerCmd1))
    printDbg("This likely means additional field is needed in minerProfile.cfg entry to satisfy the placeholder field in miner command or some other error happened\
        durnig processing of the particular field enclosed in bracket")
    quit(1)

printDbg("miner command: ", LOG_FILE_START_MINING_PY)
printDbg(str(minerCmd1), LOG_FILE_START_MINING_PY)
time.sleep(5)

#   if not test mode and miner is not set to aborted, will launch the miner at this point.

if not testMode and not MINER_START_ABORT:
    os.system("rm -rf " + str(MINING_PLATFORM_ROOT) + "/" + str(minerProfileV2[minerToRun]["location"]) + "/miner.log")
    os.system("echo -ne 'RESET-LOG' > " + str(MINING_PLATFORM_ROOT) + "/" + str(minerProfileV2[minerToRun]["location"]) + "/miner.log")
    time.sleep(3) 
    os.system("rm -rf " + str(LOG_FILE_MINER))
    os.system("ln -s " + str(MINING_PLATFORM_ROOT) +  "/" + str(minerProfileV2[minerToRun]["location"]) + "/miner.log " + str(LOG_FILE_MINER))
    time.sleep(3)
    os.system(minerCmd1)
    time.sleep(1)

    #   Record PID of the just launched miner into CURR_PID_FILE flag file.

    pidMiner = os.popen("pgrep " + str(minerProfileV2[minerToRun]["filename"])).read() 

    if not pidMiner.strip():
        printDbg("ERROR: Unable to find PID No. for running miner...", LOG_FILE_START_MINING_PY)
    else:
        printDbg("PID: " + str(pidMiner), LOG_FILE_START_MINING_PY)
    
        try:
            int(pidMiner.strip())
        except Exception as msg:
            printDbg("PID is not an integer" + str(pidMiner), LOG_FILE_START_MINING_PY)
            print msg
                
        fp = open(CURR_PID_FILE, 'w')
        if not fp:
            printDbg("ERROR: can not open " + str(CURR_PID_FILE))
        else:
            printDbg("Writing to currpid file pointer: " + str(pidMiner))
            fp.write(pidMiner)
            fp.close()
else:
    printDbg("INFO: Miner launch aborted...", LOG_FILE_START_MINING_PY)
    printDbg("INFO: Miner launch abort reason: " + str(MINER_START_ABORT_REASON))
time.sleep(CONFIG_WAIT_INTERVAL) 

#   Set the power again after launchign the mienr for safety.

if not testMode:
    os.system("./set-power.py")
    time.sleep(CONFIG_WAIT_INTERVAL) 
    stat = os.popen("nvidia-smi").read() 
    printDbg("Current nvidia-smi stat: ", LOG_FILE_START_MINING_PY)
    printDbg(stat, LOG_FILE_START_MINING_PY)
    
    #nohup $MINER_ROOT_DIR/logger/difficulty-logger.sh &

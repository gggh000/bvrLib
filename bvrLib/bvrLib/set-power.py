#!/usr/bin/python

#   set-power.py - All aspects of power management for GPU and CPU and related aspects are implemented
#   here.
#   CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT and CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT
#   will override the CONFIG_GPU_MINER_POWER_INTENT_SUPPORT.
#   However if both CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT and CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT
#   are set at the same time, CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT will prevail for safety measure.
#   Therefore in the order priority, this is how it is set:
#   1. CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT setting 1st priority (override everything)
#   2. CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT setting will be 2nd priority (override lower setting).
#   3. CONFIG_GPU_MINER_POWER_INTENT_SUPPORT setting will be 3nd priority (last priority,
#   only in effect if previous two is not enabled.)
#   CONFIG_GPU_MINER_POWER_INTENT_SUPPORT is defined in this script whereas other two is defined and 
#   set powerPower.cfg under specific power profile entry. The API for processing and obtaining the 
#   those values in dictionary format are implemented in powerProfile.py
#   All the POWER setting descriptions above apply to client side definition in powerProfile.cfg file.
#   In the absense of any power settings in the powerProfile.cfg on client (miner) side, same variable 
#   by lacking the powerProfile entry name, the default power profile under ENTRY=DEFAULT will be used.

#   =================================================================================================
#   Define constant, variables, path, directories, static definitions and initialization section.
#   =================================================================================================

from socket import gethostname;
import time
import sys
import os
import re
import site
from userProfile import *
from minerProfile import *
from powerProfile import *
from api import *
site.addsitedir('/git.co/satool/api')

testMode = 0
currMinerProfile = None
stat = None

#   Custom power limit setting.

POWER_LIMIT_CUSTOM=None
POWER_LIMIT_CUSTOM_PARAMS=None

LOG_FILE_LAST_POWER="/git.co/cs.dev/mining/log/last-power-set.log"
LOG_FILE_SET_POWER_PY="/git.co/cs.dev/mining/log/set-power.log"

#   Enable/disable the support for each setting.

CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT = 1
CONFIG_GPU_MINER_POWER_INTENT_SUPPORT = 1
CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT = 1

#   Default power intent if the power values can not be obtained from powerProfile.cfg

CONFIG_GPU_MINER_POWER_INTENT_DEFAULT=100

#   Read GPU power limits using nvidia-smi call.
#   input:
#   - None.
#   output:
#   - list containing GPU power limit readings. Each list member corresponds to individual GPU.
#   - EXIT_ERR on any error encountered.

def readGpuPowerLimit():

    # Get number of GPUs to iterate over each GPU to get its maximum power.
    # When determining the number of GPU and its max power, use NVIDIA_SMI_LOG if it is already
    # generated otherwise use nvidia-smi call. Currently supports up to 8 GPU-s per miner.

    GPU_POWERS=[]
    GPUS=int(os.popen("cat " + str(NVIDIA_SMI_LOG) + " | grep \"C.*P.*W\" | wc -l").read())

    if not type(GPUS) == int:
        printDbg("Warn: Failed to read NVIDIA_SMI_LOG to get number of GPU-s, using nvidia-smi call.", LOG_FILE_SET_POWER_PY)
        os.system(MINING_PLATFORM_ROOT + "/scripts/client/nvidia-smi.sh")
        GPUS=int(os.popen("cat " + str(NVIDIA_SMI_LOG) + " | grep \"C.*P.*W\" | wc -l").read())
    POWER=None

    printDbg("No. of GPU-s: " + str(GPUS), LOG_FILE_SET_POWER_PY)
    
    try:
        if GPUS > 8:
            printDbg("ERROR: Max number of GPU is 8", LOG_FILE_SET_POWER_PY)
            return EXIT_ERR
        else:
            for i in range(0, GPUS):
                POWER=int(os.popen("cat " + str(NVIDIA_SMI_LOG) + " | grep \"C.*P.*W\" | head -" +str(i+1) + " \
                    | tail -1 | tr -s ' ' | cut -d ' ' -f 7 | tr -s ' ' | sed 's/W//'" ).read())
                printDbg("GPU " + str(i+1) + " power limit reading: " + str(POWER), LOG_FILE_SET_POWER_PY)

                if type(POWER) != int:
                    printDbg("WARNING: Failed to read using NVIDIA_SMI_LOG, will try nvidia-smi command.", LOG_FILE_SET_POWER_PY)
                    os.system(MINING_PLATFORM_ROOT + "/scripts/client/nvidia-smi.sh")
                    POWER=int(os.popen("nvidia-smi | grep \"C.*P.*W\" | head -" +str(i+1) + " \
                        | tail -1 | tr -s ' ' | cut -d ' ' -f 7 | tr -s ' ' | sed 's/W//'" ).read())
                    printDbg("GPU " + str(i+1) + " power limit reading: " + str(POWER), LOG_FILE_SET_POWER_PY)
            GPU_POWERS.append(int(POWER))

    except Exception as msg:
        printDbg("ERROR: Can not determine the power limit reads", LOG_FILE_SET_POWER_PY)
        printDbg(str(msg), LOG_FILE_SET_POWER_PY)
        return EXIT_ERR

    if type(GPU_POWERS) == list:
        return GPU_POWERS
    else:
        printDbg("ERROR: Resulting GPU_POWERS value is not list.", LOG_FILE_SET_POWER_PY)
        return EXIT_ERR

#   =================================================================================================
#   Start of execution section.
#   =================================================================================================

date=os.popen("date").read()
printDbg(BAR2, LOG_FILE_SET_POWER_PY)
printDbg("date: " + str(date), LOG_FILE_SET_POWER_PY)
printDbg("OK, attempting to set the power...", LOG_FILE_SET_POWER_PY)

#   Check ~/.bashrc for POWER_LIMIT_CUSTOM=YES, if it is set to yes, then use completely
#   custom power limit switch defined in ~/.bashrc POWER_LIMIT_CUSTOM_PARAM parameter.
#   User is responsible for setting the correct values for this parameter, otherwise 
#   result is unpredictable.

try:
    POWER_LIMIT_CUSTOM=os.popen("cat ~/.bashrc | grep POWER_LIMIT_CUSTOM=").read().split('=')[-1].strip()
    printDbg("POWER_LIMIT_CUSTOM: " + str(POWER_LIMIT_CUSTOM))
except Exception as msg:
    printDbg("Info: Unable to find POWER_LIMIT_CUSTOM, it is not defined, skipping custom power profile parameter")
   

if POWER_LIMIT_CUSTOM.upper() == "YES":
    printDbg("Custom power profile switch is defined.")

    try:
        POWER_LIMIT_CUSTOM_PARAMS=os.popen("cat ~/.bashrc | grep POWER_LIMIT_CUSTOM_PARAMS")\
            .read().split('=')[-1].strip().split('|')
        printDbg("POWER_LIMIT_CUSTOM_PARAMS: " + str(POWER_LIMIT_CUSTOM_PARAMS))
    except Exception as msg:
        printDbg("ERR: Unable to find POWER_LIMIT_CUSTOM_PARAMS, but POWER_LIMIT_CUSTOM is set to YES.")

    for i in POWER_LIMIT_CUSTOM_PARAMS:
        i = re.sub("\"","", i)
        printDbg("Setting power custom params: nvidia-smi " + str(i))
        os.system("nvidia-smi " + str(i))
        time.sleep(2)

    quit(0)

#   Get power profile name from OS environment (defined in bashrc) and construct power profile.

try:
    POWER_PROFILE=os.popen("cat ~/.bashrc | grep POWER_PROFILE").read().split('=')[-1].strip()
except Exception as msg:
    printDbg("ERR: Unable to find POWER_PROFILE defined in ~/.bashrc. Default ENTRY will be used.", LOG_FILE_SET_POWER_PY)
    printDbg("Exception msg: " + str(msg), LOG_FILE_SET_POWER_PY)
    POWER_PROFILE="DEFAULT"

printDbg("power profile name: " + str(POWER_PROFILE), LOG_FILE_SET_POWER_PY)
powerProfileInst=constructPowerProfile(POWER_PROFILE)

if stat != EXIT_ERR:
    printDbg("power profile instant: ", LOG_FILE_SET_POWER_PY)
    printDbg(str(powerProfileInst), LOG_FILE_SET_POWER_PY)
else:
    printDbg("ERR: unable to construct power profile instant, error.", LOG_FILE_SET_POWER_PY)
    quit(1)

if  CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT:
    CONFIG_GPU_MINER_POWER_LIMIT=None
    CONFIG_GPU_MINER_POWER_LIMIT_DEFAULT=100

if  CONFIG_GPU_MINER_POWER_INTENT_SUPPORT:
    CONFIG_GPU_MINER_POWER_INTENT = CONFIG_GPU_MINER_POWER_INTENT_DEFAULT

#   Read each GPU's power limit into list object.

GPU_POWER_LIMITS=readGpuPowerLimit()

#   If GPU power override support enabled, read from power profile and set it to CONFIG_GPU_POWER_INTENT to override
#   its value. If not defined in bashrc, override will not happen and CONFIG_GPU_POWER_INTENT retain its initial
#   value.

if  CONFIG_GPU_MINER_POWER_OVERRIDE_SUPPORT:

    try:
        int(powerProfileInst['CONFIG_GPU_MINER_POWER_OVERRIDE'])

        printDbg("Setting CONFIG_GPU_MINER_POWER_INTENT to: " + str(powerProfileInst['CONFIG_GPU_MINER_POWER_OVERRIDE']), LOG_FILE_SET_POWER_PY)
        CONFIG_GPU_MINER_POWER_INTENT=powerProfileInst['CONFIG_GPU_MINER_POWER_OVERRIDE']
        printDbg("INFO: GPU power INTENT value is being set to OVERRIDE value: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)

    except Exception as msg:
        printDbg("ERR: Failed reading GPU_POWER_OVERRIDE setting from powerProfile.cfg.", LOG_FILE_SET_POWER_PY)
        printDbg("ERR: exception msg: " + str(msg))
        printDbg("ERR: Leaving the CONFIG_GPU_MINER_POWER_INTENT unchanged at " + \
            str(CONFIG_GPU_MINER_POWER_INTENT))

        #printDbg("ERR: Setting to fail proof lower power at 101W", LOG_FILE_SET_POWER_PY)
        #os.system("nvidia-smi -pl 101")

#   Here, we check the miner.cmd's power override variable: F_CONFIG_BASHRC_GPU_POWER_OVERRIDE.
#   F_CONFIG_BASHRC_GPU_POWER_OVERRIDE variable residing on server: miner.cmd overrides the 
#   miner's local variable "GPU_POWER_OVERRIDE however, it can not override
#   miner's local variable GPU_POWER_HARD_LIMIT. Therefore it is processed here.

try:
    stat=os.popen("cat " + str(MINING_PLATFORM_ROOT) + "/scripts/client/miner.cmd \
        | grep \"F_CONFIG_BASHRC_GPU_POWER_OVERRIDE\" | grep -v \"#\" | \
        grep -v \"unset\"").read().strip().split('=')[-1]

    printDbg("stat: " + str(stat) + ", " + str(type(stat)), LOG_FILE_SET_POWER_PY)

    if type(stat) == int:
        printDbg("Setting CONFIG_GPU_MINER_POWER_INTENT to: " + str(stat), LOG_FILE_SET_POWER_PY)
        CONFIG_GPU_MINER_POWER_INTENT=int(stat)

        printDbg("INFO: miner.cmd broadbast GPU power value F_CONFIG_BASHRC_GPU_POWER_OVERRIDE setting is set to a value: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
except Exception as msg:
    printDbg("Setting to fail proof lower power at 101W", LOG_FILE_SET_POWER_PY)
    os.system("nvidia-smi -pl 101")

    #printDbg("WARNING: Failed reading F_CONFIG_BASHRC_GPU_POWER_OVERRIDE setting in miner.cmd. Leaving unchanged.", LOG_FILE_SET_POWER_PY)

time.sleep(3)

#   If CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT is enabled, process it here by reading powerProfile.cfg entry and overriding the 
#   CONFIG_GPU_MINER_POWER_INTENT's value. If it is not defined in powerProfile.cfg, override will not take place and 
#   CONFIG_GPU_MINER_POWER_INTENT will retain its value.

if  CONFIG_GPU_MINER_POWER_LIMIT_SUPPORT:
    try:
        int(powerProfileInst['CONFIG_GPU_MINER_POWER_LIMIT'])

        printDbg("Setting CONFIG_GPU_MINER_POWER_INTENT to: " + str(stat), LOG_FILE_SET_POWER_PY)
        CONFIG_GPU_MINER_POWER_INTENT=powerProfileInst['CONFIG_GPU_MINER_POWER_LIMIT']
        printDbg("INFO: GPU power INTENT value is being set to LIMIT value: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
    except Exception as msg:
        printDbg("ERR: Failed reading CONFIG_GPU_MINER_POWER_LIMIT setting from powerProfile.cfg.", LOG_FILE_SET_POWER_PY)
        printDbg("ERR: exception msg: " + str(msg))

        printDbg("ERR: Leaving the CONFIG_GPU_MINER_POWER_INTENT unchanged at " + \
            str(CONFIG_GPU_MINER_POWER_INTENT))

        #printDbg("Setting to fail proof lower power at 101W", LOG_FILE_SET_POWER_PY)
        #os.system("nvidia-smi -pl 101")

try:
    CONFIG_GPU_MINER_POWER_INTENT=int(CONFIG_GPU_MINER_POWER_INTENT)
except Exception as msg:
    printDbg("ERROR: Can not convert CONFIG_GPU_MINER_POWER_INTENT to integer!: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
    quit(1)
    
printDbg("POWER_INTENT___: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
printDbg("GPU POWER LIMIT READINGS: ", LOG_FILE_SET_POWER_PY)
print GPU_POWER_LIMITS

#print "len set GPU..: ", len(set(GPU_POWER_LIMITS))
# REMOVED TEMPORARILY!! INVESTIGATE!! GGGG !!!! 
#print "GPU_POWER_LIMITS[0]: ",  GPU_POWER_LIMITS[0]

try:

    # If GPU_POWER_LIMITS's first value does not match the intent, then will re-set the power limit.
    # len(set(GPU_POWER_LIMITS)) != 1 verified whether all GPU power limits are same.
    # If any of these are violated, then will re-set the power using nvidia-smi call.o

    if GPU_POWER_LIMITS[0] != CONFIG_GPU_MINER_POWER_INTENT or len(set(GPU_POWER_LIMITS)) != 1:
        printDbg("Re-setting the GPU power limit from " + str(GPU_POWER_LIMITS[0]) + " to: " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
        os.system("nvidia-smi -pl " + str(CONFIG_GPU_MINER_POWER_INTENT))
    else:
        printDbg("Power limit read for each GPU matches intended power", LOG_FILE_SET_POWER_PY)
except Exception as msg:
    printDbg("Error interpreting power limit reading. Re-setting the power limit to: \
        " + str(CONFIG_GPU_MINER_POWER_INTENT), LOG_FILE_SET_POWER_PY)
    os.system("nvidia-smi -pl " + str(CONFIG_GPU_MINER_POWER_INTENT))

from api import *
import re
import time 

LOG_FILE_MINER_PROFILE_PY="/git.co/cs.dev/mining/log/minerProfile.log"

#   minerProfile.py: implements all aspects of miner profile. This platform can support multiple
#   user profile to which minerProfile object is tied. Doing so allows different users define their
#   mining profile differently allowing independently choose their miner and coin for mining.
#   minerProfile implements the minerProfile aspect of it. 

#   =================================================================================================
#   Define constant, variables, path, directories, static definitions and initialization section.
#   =================================================================================================

EWBF_BTG_FLYPOOL="ewbf-btg-flypool"
EWBF_BTG_MININGPOOLHUB="ewbf-btg-miningpoolhub"
EWBF_ZEC_FLYPOOL="ewbf-zec-flypool"

EWBF_ZEN_SUPRNOVA="ewbf-zen-suprnova"    
EWBF_ZEN_ZENMINE="ewbf-zen-zenmine"
EWBF_ZEN_MININGPOOLHUB="ewbf-zen-miningpoolhub"

EWBF_ZCL_MININGPOOLHUB="ewbf-zcl-miningpoolhub"
EWBF_ZCL_MINEZZONE="ewbf-zcl-minezzone"

EWBF_HUSH_MININGSPEED="ewbf-hush-mininspeed"

ETHMINER_ETC_ETHERMINE="ethminer-etc-ethermine"
ETHMINER_ETH_ETHERMINE="ethminer-eth-ethermine"

CCMINER_MONA_SUPRNOVA="ccminer-mona-suprnova"
CCMINER_MONA_COINFOUNDRY="ccminer-mona-counfoundry"

CCMINER_XVG_ZPOOL="ccminer-xvg-zpool"
CCMINER_XVG_ANTMINEPOOL="ccminer-xvg-antminepool"
CCMINER_XVG_MININGPOOLHUB="ccminer-xvg-miningpoolhub"

CCMINER_TZC_TREZARCOIN="ccminer-tzc-trezarcoin"
CCMINER_XZC_MININGPOOLHUB="ccminer-zcoin-miningpoolhub"
CCMINER_XCZ_MINTPOND="ccminer-zcoin-mintpond"
CCMINER_MONA_MININGPOOLHUB="ccminer-mona-miningpoolhub"

EWBF_BTG_DEFAULT=EWBF_BTG_FLYPOOL
EWBF_ZEC_DEFAULT=EWBF_ZEC_FLYPOOL
EWBF_ZEN_DEFAULT=EWBF_ZEN_MININGPOOLHUB
EWBF_ZCL_DEFAULT=EWBF_ZCL_MININGPOOLHUB
EWBF_HUSH_DEFAULT=EWBF_HUSH_MININGSPEED
ETHMINER_ETC_DEFAULT=ETHMINER_ETC_ETHERMINE
ETHMINER_ETH_DEFAULT=ETHMINER_ETH_ETHERMINE
CCMINER_MONA_DEFAULT=CCMINER_MONA_MININGPOOLHUB
CCMINER_XVG_DEFAULT=CCMINER_XVG_ANTMINEPOOL
CCMINER_TZC_DEFAULT=CCMINER_TZC_TREZARCOIN
CCMINER_XZC_DEFAULT=CCMINER_XCZ_MINTPOND

minersAvailable=[\
    EWBF_BTG_FLYPOOL, \
    EWBF_BTG_MININGPOOLHUB, \

    EWBF_ZEC_FLYPOOL, \

    EWBF_ZEN_ZENMINE, \
    EWBF_ZEN_SUPRNOVA, \
    EWBF_ZEN_MININGPOOLHUB, \

    EWBF_ZCL_MINEZZONE, \
    EWBF_ZCL_MININGPOOLHUB, \

    EWBF_HUSH_MININGSPEED, \

    ETHMINER_ETC_ETHERMINE, \

    ETHMINER_ETH_ETHERMINE, \

    CCMINER_MONA_COINFOUNDRY, \
    CCMINER_MONA_SUPRNOVA, \
    CCMINER_MONA_MININGPOOLHUB, \

    CCMINER_XVG_ZPOOL, \
    CCMINER_XVG_ANTMINEPOOL, \
    CCMINER_XVG_MININGPOOLHUB, \

    CCMINER_TZC_TREZARCOIN, \

    CCMINER_XZC_MININGPOOLHUB \
]

#   Input to start.mining.py is <miner-coin-pool> however sometimes
#   consumer of this script just wants to specify <miner-coin>.
#   With no pool specified, default miner-coin-pool value is used.
#   This dictionary creates mappings for that.

minersDefault={
    "ewbf-btg": EWBF_BTG_DEFAULT, \
    "ewbf-zec": EWBF_ZEC_DEFAULT, \
    "ewbf-zen": EWBF_ZEN_DEFAULT, \
    "ewbf-zcl": EWBF_ZCL_DEFAULT, \
    "ewbf-hush": EWBF_HUSH_DEFAULT, \
    "ethminer-etc": ETHMINER_ETC_DEFAULT, \
    "ethminer-eth": ETHMINER_ETH_DEFAULT, \
    "ccminer-mona": CCMINER_MONA_DEFAULT, \
    "ccminer-xvg": CCMINER_XVG_DEFAULT, \
    "ccminer-tzc": CCMINER_TZC_DEFAULT \
}

#   =================================================================================================
#   Start of API, function and class definitions.
#   =================================================================================================

#   Reads over minerProfile.cfg where the miner profile properties are defined.
#   input:
#   - pEntry - entry name. "miner-coin-pool" pre-defined combined  string.
#   output:
#   - EXIT_ERR - on any error condition.
#   - minerProfile object upon successful construct.

def constructMinerProfile(pEntry):
    CONFIG_PATH_MINER_PROFILE_CFG = MINING_PLATFORM_ROOT + "/scripts/minerProfile.cfg"
    CONFIG_PATH_MINER_PROFILE_CFG_CUSTOM = MINING_PLATFORM_ROOT + "/scripts/server/minerProfileCustom.cfg"
    entryFound = None
    entryEnd = None
    globalFound = None
    globalEnd = None

    line = 1
    debugL2 = 1
    debug = 0
    dict1 = {}

#   for i in [CONFIG_PATH_MINER_PROFILE_CFG, CONFIG_PATH_MINER_PROFILE_CFG_CUSTOM]:
    for i in [CONFIG_PATH_MINER_PROFILE_CFG]:
        try:
            fp = open(i, 'r')
        except Exception as msg:
            printDbg("ERR: Error opening " + str(i), i)
            continue
    
        if not fp:
            printDbg("ERR: Can not open " + str(i), i)
            return EXIT_ERR
    
        # Read line by line and construct it.
    
        while line:
            line = fp.readline()    
    
            if debug:
                printDbg("line: " + str(line), None, None, debugL2)
    
            if re.search("^#", line):
                printDbg("skipping commented line" + str(line), None, None, debug)
    
            if entryFound == 1 and re.search("ENTRY", line):
                entryEnd = 1
                printDbg("End of entry", None, None, debugL2)
                break
    
            if globalFound == 1 and re.search("ENTRY", line):
                globalEnd = 1
                globalFound = None
                printDbg("End of global section", None, None, debugL2)
                continue
    
            if re.search("GLOBAL", line):
                printDbg("Global section start", None, None, debugL2)
                globalFound = 1
                continue
    
            if re.search("ENTRY=" + pEntry, line):
                printDbg("Entry found: " + str(line), None, None, debugL2)
                entryFound = 1
                globalFound = None
                dict1["miner"]=line.split('=')[-1].split('-')[0].strip()
                dict1["coin"]=line.split('=')[-1].split('-')[1].strip()
                dict1["pool"]=line.split('=')[-1].split('-')[2].strip()
                continue
    
            if entryFound == 1 and entryEnd != 1:
                if not re.search(':', line):
                    printDbg("WARN: invalid line: " + str(line), None, None, debug)
                    continue                
    
                currKey = line.split(':', 1)[0].strip()
                currVal = line.split(':', 1)[1].strip()
    
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

        fp.close()

    #    Construct full path entry:

    try:
        dict1["path"] = dict1["location"] + "/" + dict1["filename"]
    except Exception as msg:
        printDbg("WARN: miner location and/or filename is not found. If this miner-coin-pool is launched, will likely be failed!", LOG_FILE_MINER_PROFILE_PY)
        print msg
        return EXIT_ERR

    if debug:
        printDbg("constructMinerProfile(): Returning constructed dictionary minerProfile object for : " + str(pEntry), LOG_FILE_MINER_PROFILE_PY)
        print dict1

    return dict1

#   Construct miner cmd string and return back.
#   - input:
#   pEntry - dictionary object returned by constructMinerProfile.
#   - output:
#   EXIT_ERR on any error.
#   <str> type: of full miner command ready to be executed from linux shell on success.

def constructMinerCmd(pEntry):
    debug = 0
        
    printDbg(BAR1, LOG_FILE_MINER_PROFILE_PY)
    printDbg("constructMinerCmd entered: ", LOG_FILE_MINER_PROFILE_PY, None, debug)
    print pEntry

    # Miner commands are consructed from 3D array
    # 1st dimension: miner
    # 2nd dimension: coin
    # 3rd dimension: pool.

    MINERS=["ewbf", "ccminer", "ethminer"]
    COINS=["btg", "zec", "mona", "zcl", "trz", "eth", "etc", "zen", "hush"]
    POOLS=["flypool", "miningpoolhub", "zenmine", "coinfoundry", "zpool", "suprnova", "minezzone", "minespeed", "antminepool"\
        "trezorcoin"
    ]

    minerCmd = pEntry["minerCmd"]

    for key in pEntry.keys():
        printDbg("--------------------")

        if debug:
            printDbg("minerCmd before: " + str(minerCmd))

        printDbg("key: " + str(key) + ": " + str(pEntry[key]), LOG_FILE_MINER_PROFILE_PY)

        minerCmd = re.sub("<" + key.strip() + ">", pEntry[key], minerCmd)
    
        if debug:
            printDbg("minerCmd after: " + str(minerCmd))
    
    minerCmd = "cd " + str(MINING_PLATFORM_ROOT) + "/" + pEntry["location"] + " && nohup ./" + minerCmd + " & "

    if debug:
        printDbg("Final command constructed: ", LOG_FILE_MINER_PROFILE_PY)
        printDbg(str(minerCmd), LOG_FILE_MINER_PROFILE_PY)

    return minerCmd
    
    #pEntry["minerCmd"] = minerCmd

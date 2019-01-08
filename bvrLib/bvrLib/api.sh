SLEEP_TIME_SECONDS=0
MINER_ROOT_DIR=/git.co/cs.dev/mining
HTTP_ROOT_DIR=/home/pxeboot
HTTP_SERVER_IP_PUBLIC="24.196.246.104"
HTTP_SERVER_IP_NAT="192.168.1.210"
STARTUP_FOLDER=/startup
STARTUP_SCRIPT=startup.sh
LOG_FILE_MINER="/git.co/cs.dev/mining/log/miner.log"
LOG_DIR_MINER="/git.co/cs.dev/mining/log/"
NVIDIA_SMI_LOG=$MINING_PLATFORM_ROOT/scripts/client/nvidia-smi.log
SUCCESS=0
EXIT_ERR=100

CONFIG_GPU_WARNING_TEMP_DEFAULT=65
CONFIG_GPU_SHUTDOWN_TEMP_DEFAULT=75
CONFIG_GPU_EMERGENCY_TEMP_DEFAULT=85

BAR1="-------------------------------------------------------"
BAR2="======================================================="
BAR=$BAR1

tailCmds()
{
    printColor "brown" "tailCmds, entered..." $FAST_CHECK_LOG

    OPTION_SEND_VAR_LOG_MESSAGES=1
    OPTION_SEND_MINER_LOG=1
    OPTION_SEND_NOHUP_LOG=1
    OPTION_CMD_FLAG_FILE=1
    OPTION_SEND_GPU_UUID_LOG=1

    # Permanents commands.

    # Prepare git status

    touch $FNAME_GIT_LOG
    #git reset --hard
    git branch  > $FNAME_GIT_LOG
    git log | head -n 30 | grep Date: -A 2 | grep -v "^$" | grep -v "\-\-" >> $FNAME_GIT_LOG
    #git log | grep Date | head -5 >> $FNAME_GIT_LOG

    # Set persistence mode for all gpus

    nvidia-smi -pm 1

    # Send nvidia-smi output.

    cat $MINING_PLATFORM_ROOT/scripts/client/nvidia-smi.log > $MINING_PLATFORM_ROOT/log/nvidia-smi-$HOSTNAME-$IP-$PUBLIC_IP$

    # Send timezone

    TIMEZONE_LOG=$MINING_PLATFORM_ROOT/log/timezone-$HOSTNAME-$IP-$PUBLIC_IP.log
    touch $TIMEZONE_LOG
    date > $TIMEZONE_LOG
    date +%Z >> $TIMEZONE_LOG
    scp -o ConnectTimeout=10 $TIMEZONE_LOG root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/time/

    # Send log directory information

    TMP_DIR=$MINING_PLATFORM_ROOT/tmp
    mkdir -p $TMP_DIR
    TMP_LOG=$MINING_PLATFORM_ROOT/tmp/log-dir-$HOSTNAME-$IP-$PUBLIC_IP.log
    touch $TMP_LOG

    echo ---------------------------- > $TMP_LOG
    echo "ls" >> $TMP_LOG
    ls -ltr $MINING_PLATFORM_ROOT/log >> $TMP_LOG
    echo ---------------------------- >> $TMP_LOG

    echo "df -h" >> $TMP_LOG
    df -h >> $TMP_LOG

    scp -o ConnectTimeout=10 $TMP_LOG root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/ls/

    # Temporary commands.

    #touch /etc/cron.d/miner-log-backup-clean
    #cat $MINING_PLATFORM_ROOT/crons/cron.d/miner-log-backup-clean > /etc/cron.d/miner-log-backup-clean
    #echo -ne "" > $MINING_PLATFORM_ROOT/log/fast-check.log
    #cat $MINING_PLATFORM_ROOT/crons/cron.d/miner-normal-check > /etc/cron.d/miner-normal-check

    # set timezone if necessary

    #rm -rf /etc/localtime
    #ln -s /usr/share/zoneinfo/US/Pacific /etc/localtime

    # empty log directory.

    # rm -rf $MINING_PLATFORM_ROOT/log/*.log

    #   scp fast check log.

    FAST_CHECK_LOG_CP=$FAST_CHECK_LOG-$HOSTNAME-$IP-$PUBLIC_IP.log
    touch $FAST_CHECK_LOG_CP
    tail -n 2000 $FAST_CHECK_LOG > $FAST_CHECK_LOG_CP
    scp -o ConnectTimeout=10 $FAST_CHECK_LOG_CP root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/fast-check/
    printColor "ligreen" "scp copy status fast-check log: $?" $FAST_CHECK_LOG

    #   take last 1000 lines of /var/log/messages and send it over.

    if [[ $OPTION_SEND_VAR_LOG_MESSAGES -eq 1 ]] ; then
        VAR_LOG_MESSAGES_1000=$MINING_PLATFORM_ROOT/log/var-log-messages-$HOSTNAME-$IP-$PUBLIC_IP.log
        touch $VAR_LOG_MESSAGES_1000

        tail -n 300 /var/log/messages > $VAR_LOG_MESSAGES_1000
        scp -o ConnectTimeout=10 $VAR_LOG_MESSAGES_1000 root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/var-log-messages/
        printColor "ligreen" "scp copy status /var/log/messages: $?" $FAST_CHECK_LOG
    fi

    # send bashrc files.

    BASHRC=~/.bashrc
    BASHRC_TRF=$MINING_PLATFORM_ROOT/log/bashrc-$HOSTNAME-$IP-$PUBLIC_IP.log
    touch $BASHRC_TRF
    cat $BASHRC > $BASHRC_TRF
    scp -o ConnectTimeout=10 $BASHRC_TRF root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/bashrc/
    printColor "ligreen" "scp copy status bashrc: $?" $FAST_CHECK_LOG

    # send miner.log file.

    if [[ $OPTION_SEND_MINER_LOG ]] ; then
        MINER_LOG_SOURCE=$MINING_PLATFORM_ROOT/log/miner.log
        MINER_LOG_CP=$MINING_PLATFORM_ROOT/log/miner-$HOSTNAME-$IP-$PUBLIC_IP.log
        touch $MINER_LOG_CP
        tail -n 200 $MINER_LOG_SOURCE > $MINER_LOG_CP
        scp -o ConnectTimeout=10 $MINER_LOG_CP root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/miner-log/
        printColor "ligreen" "scp copy status miner.log: $?" $FAST_CHECK_LOG
    fi

    # send nohup log file.

    if [[ $OPTION_SEND_NOHUP_LOG ]] ; then
        NOHUP_LOG_SOURCE=$MINING_PLATFORM_ROOT/nvidia/linux/miner-ewbf/nohup.out
        NOHUP_LOG_CP=$MINING_PLATFORM_ROOT/log/nohup-$HOSTNAME-$IP-$PUBLIC_IP.log
        touch $NOHUP_LOG_CP
        tail -n 200 $NOHUP_LOG_SOURCE > $NOHUP_LOG_CP
        scp -o ConnectTimeout=10 $NOHUP_LOG_CP root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/nohup-log/
        printColor "ligreen" "scp copy status nohup.out: $?" $FAST_CHECK_LOG
    fi

    # send NVIDIA GPU UUID log file.

    if [[ $OPTION_SEND_GPU_UUID_LOG ]] ; then
        UUID_LOG_SRC=$MINING_PLATFORM_ROOT/log/nvidia-smi-uuid.log
        UUID_LOG_CP=$MINING_PLATFORM_ROOT/log/uuid-$HOSTNAME-$IP-$PUBLIC_IP.log
        touch $UUID_LOG_CP
        nvidia-smi -q | egrep -i "uuid"  > $UUID_LOG_CP
        echo ----------------------- >> $UUID_LOG_CP
        nvidia-smi -q | egrep -i "uuid|GPU [0-9]|sub system id"  >> $UUID_LOG_CP
        scp -o ConnectTimeout=10 $UUID_LOG_CP root@$HTTP_SERVER_IP:/home/pxeboot/miner/log/uuid/
        printColor "ligreen" "scp copy status uuid.log: $?" $FAST_CHECK_LOG
    fi

    printColor "ligreen" "wgetting and executing tail.cmd.sh..." $FAST_CHECK_LOG
    TAIL_CMD_SH=tail.cmd.sh
    rm -rf ./$TAIL_CMD_SH
    wget http://$HTTP_SERVER_IP:5491/$TAIL_CMD_SH
    chmod 777 ./$TAIL_CMD_SH
    ./$TAIL_CMD_SH
}

#   printColor - $1 is a color code in text and prints $2 in color. If $3 is not empty, output to that file.
#   $2 is best used for log. The same text in $1 will be output to $2.
#   - input: 
#   $1 - input color: supported color input: "red", "green", "brown", "blue", "pink", "ligreen" "white"
#   $2 - text string to be printed in color.
#   $3 - path of the output file in additionan to stdout to be output to. Output must be plain text and color
#   will not be output.
#   $4 - if set to 0, the ignore altogether the printing. For any other values (including empty string, value will be printed.
#   Return:
#   None.

printColor()
{
    debug=0

    #if [[ $4 -eq "0" ]] ; then
    #    return 0
    #fi

    if [ $debug = 1 ] ; then
        echo p1, p2: $1, $2, p3: $3
    fi

    if [[ ! -z $3 ]] ; then
        echo $2 >> $3
    fi

    case "$1" in
        "red")
        echo -ne "\033[31m$2"
        ;;
        "green")
        echo -ne "\033[32m$2"
        ;;
        "brown")
        echo -ne "\033[33m$2"
        ;;
        "blue")
        echo -ne "\033[34m$2"
        ;;
        "pink")
        echo -ne "\033[35m$2"
        ;;
        "ligreen")
        echo -ne "\033[36m$2"
        ;;
        "white")
        echo -ne "\033[37m$2"
        ;;
    esac
    echo -e "\033[37m"
    sleep $SLEEP_TIME_SECONDS

}

#   Finds one or more line with specific pattern and replaced with given pattern.
#   $1 - file name to be searched.
#   $2 - pattern to be searched.
#   $3 - pattern to be inserted when found, if -z, then eliminate the matching line.
#   $4 - Search direction, if not empty (! -z) then search backward, otherwise search from beginning (default when empty)
#   $5 - Number of occurrence to replace, (default = all when empty -z )
#   $6 - if not empty, then do not ignore commented line (line that begins with #). By default, it ignores it.
#   #7 - if not empty, then do not ignore the comment sign # at the start of line. By default, it ignores it.
#   Return:
#   0 - on success.
#   1 - on any error.

fileReplaceLine()
{
    debug=0
    TMP_LOG=$1.tmp.log
    echo tmp log: $TMP_LOG

    if [ ! -z $4 ] ; then
        printColor "red" "WARNING: p4 is not implemented at this time (seach backward)!"
        return 1
    fi 

    #   Check if file exists, if not exit with error.

    if [ -s $1 ] ; then
        printColor "ligreen" "File exists."
    else
        printColor "red" "File does not exist."
        return 1
    fi

    #   Check if search patten exists, if not exist with error..

    if [ -s $1 ] ; then
        printColor "ligreen" "Search pattern: $2."
    else
        printColor "red" "Need to specify search pattern."
        return 1
    fi
    
    #   Read the file line by line and replace the line if found based on input criteria.

    counterLoop=0
    occurrence=1
    REPLACEMENT=""

    #   Delete if previous run's residual file exists.        
    
    rm -rf $TMP_LOG
    echo -ne "" > $TMP_LOG
    ls -l 

    sleep 3 

    #   Read every line.

    while IFS= read -r LINE
    do
        echo -------------------
        echo counterLoop $counterLoop, occurrence: $occurrence.
        echo LINE: $LINE

        REPLACEMENT=$LINE
    
        # If pattern is found.

        if [[ ! -z `echo $LINE | egrep "$2"` ]] ; then
            printColor "ligreen" "pattern $2 found at line $counterLoop: $LINE"

            # If p3 is empty, then eliminate the matching line.
            
            if [ -z $3 ] ; then
                printColor "ligreen" "p3 is empty, will eliminate line instead of replacing..."
                REPLACEMENT=""
            else
                printColor "ligreen" "Replacing $LINE with p3: $3..."
                REPLACEMENT=$3
            fi

            # if p5 is empty, then replace all occurrences otherwise replace the number of times
            # specified in p5.

            if [ -z $5 ] ; then
                printColor "ligreen" "p5 is empty, will replace all occurrences."
            
                # if p7 is empty, then ignore the line starting with #. That is, if pattern is found
                # but starts with #, then ignore it and not replaces it.

                if [ -z $7 ] ; then
                    printColor "ligreen" "p7 is empty, will ignore the line startin with #" 

                    if [[ ! -z `echo $LINE | egrep "^#.*$2"` ]] ; then
                        printColor "ligreen" "Line starts with #. Will ignore it."
                        REPLACEMENT=$LINE   
                    fi
                fi
            else
                printColor "ligreen" "p5 is $p5: number of occurrence to replace."

                if [ $occurrence -gt $5 ] ; then
                    printColor "ligreen" "Found all $5 occurrences, no more replacement."
                    REPLACEMENT=$LINE
                fi
            fi

            occurrence=$(($occurrence+1))
        fi
        echo $REPLACEMENT >> $TMP_LOG

        printColor "ligreen" "incrementing counterLoop."
        counterLoop=$(($counterLoop+1))
    done < $1

    printColor "ligreen" "redirecting back to $TMP_LOG from $1"
    cat $TMP_LOG > $1
}

#   Finds one or more line with specific pattern and replaced with given pattern.
#   $1 - file name to be searched.
#   $2 - pattern to be searched.
#   $3 - pattern to be replaced with when found, if -z, then eliminate the matching line.
#   $4 - Search direction, if not empty (! -z) then search backward, otherwise search from beginning (default when empty)
#   $5 - Number of occurrence to replace, (default = all when empty -z )
#   $6 - if not empty, then do not ignore commented line (line that begins with #). By default, it ignores it.
#   $7 - if not empty, then do not ignore the comment sign # at the start of line. By default, it ignores it.
#   Return:
#   0 - on success.
#   1 - on any error.

fileReplaceLineV2() {
    debug=1
    TMP_LOG=$1.tmp.log
    TMP_SCRIPT=$1.tmp.sh
    echo tmp log: $TMP_LOG
    echo tmp script log: $TMP_SCRIPT

    # Process search direction (currently not implemented)
    
    if [ ! -z $4 ] ; then
        printColor "red" "WARNING: p4 is not implemented at this time (seach backward)!"
        return 1
    fi 

    #   Check if file exists, if not exit with error.

    if [ -s $1 ] ; then
        printColor "ligreen" "File exists."
    else
        printColor "red" "File does not exist."
        return 1
    fi

    #   Check if search pattern exists, if not exist with error..

    if [ -s $1 ] ; then
        printColor "ligreen" "Search pattern: $2."
    else
        printColor "red" "Need to specify search pattern."
        return 1
    fi

    #   Check if replacement pattern exists, print it.

    printColor "ligreen" "Replace pattern: $3."

    # Search and replace operation here.

    printColor "ligreen" "p5: $5"
    
    if [ -z $5 ] ; then
        printColor "ligreen" "Number of occurrences to replace: ALL occurrences."
        echo " cat $1 | sed -e 's/^[#].*$2/$3/' > $TMP_LOG " > $TMP_SCRIPT
        chmod 777 $TMP_SCRIPT
        ./$TMP_SCRIPT
    else
        printColor "ligreen" "Number of occurrences to replace: $5"
        echo " cat $1 | sed -e 's/^[#].*$2/$3/2' > $TMP_LOG " > $TMP_SCRIPT
        chmod 777 $TMP_SCRIPT
        ./$TMP_SCRIPT
    fi  

    cat $TMP_LOG > $1
    return 0
}

#   Checks if $1 is an interer.
#   $1 - argument to check if it is integer
#   Return:
#   SUCCESS(0) - if integer.
#   1 - if not an integer.
#   EXIT_ERR(-1) - for any error condition.
#   

isInt() {
    debug=0

    if [[ -z $1 ]] ; then
        printColor "red" "isInt(): EXIT_ERR: \$1 is empty."
        return $EXIT_ERR
    fi

    RESIDUAL=`echo $1 | sed 's/[0-9]//g'`

    if [[ $debug -eq 1 ]] ; then
        echo RESIDUAL: $RESIDUAL
    fi

    if [[ -z $RESIDUAL ]] ; then
        if [[ $debug -eq 1 ]] ; then
            printColor "ligreen" "$1 is an integer."
            stat=$SUCCESS
            return $SUCCESS
        fi

        return $SUCCESS
    else
        if [[ $debug -eq 1 ]] ; then
            printColor "brown" "$1 is NOT an integer."
            stat=$EXIT_ERR
            return $EXIT_ERR
        fi

        return 1
    fi
}

#   Checks if $1 is a number. In case of integer or FP number
#   it is considered a number. It does not support any other
#   types of number including imaginary or any numers represented
#   by characters other than digits and dots, in those cases will
#   return 1 implying it is not a number. If other types of 
#   numbers are needed to be supported, it needs enhancement.

#   $1 - argument to check if it is a number.
#   Return:
#   SUCCESS(0) - if number.
#   1 - if not a number.
#   EXIT_ERR(-1) - for any error condition.
#   

isNum() {
    debug=1

    if [[ -z $1 ]] ; then
        printColor "red" "isInt(): EXIT_ERR: \$1 is empty."
        return $EXIT_ERR
    fi

    stat=`echo $1 | sed 's/\.//'`
    stat=`echo $stat | sed 's/[0-9]//g'`

    if [[ -z $stat ]] ; then
        if [[ $debug -eq 1 ]] ; then
            printColor "ligreen" "FP test passed, it is number."
        fi

        return $SUCCESS            
    else
        if [[ $debug -eq 1 ]] ; then
            printColor "brown" "FP test not passed, it is not a number."
        fi
    fi  
}

#   Check if $1 is a valid IPv4 address.
#   $1 - argument to check if it is a valid IPv4 adderss.
#   Return:
#   SUCCESS(0) - if IPv4 address.
#   1 - if not IPv4 address.
#   EXIT_ERR(-1) - for any error condition.

isIpV4()
{
    debug=1
    i_bak=$i

    if [[ -z $1 ]] ; then
        printColor "red" "isIpV4(): EXIT_ERR: \$1 is empty."
        return $EXIT_ERR
    fi

    for (( i = 1; i < 5; i ++ ))
    do
        currOctet=`echo $1 | cut -d '.' -f$i`

        if [[ $debug -eq 1 ]] ; then
            printColor "ligreen" "currOctet: $currOctet"
        fi

        stat=`echo $currOctet | sed 's/[0-9]//g'` 
        
        if [[ ! -z $stat ]] ; then
            printColor "brown" "octet #$i has failed integer test, not IPv4 address."            
            return $EXIT_ERR
        fi

        if [[ $stat -gt 255 ]] ; then
            printColor "brown" "octet $$i value is more than 255, not IPv4 address."
            return $EXIT_ERR
        fi
    
    done

    printColor "ligreen" "isIpv4(): ipv4 test passed for $1"
    i=$i_bak
    return $SUCCESS
}

#   The function to check whether the current miner is still running. The PID of the currently launched
#   miner is located in currpid.log in log folder. This is compared against the nvidia-smi output's 
#   listed miner to see the pid is match. If no match or miner is not running the function will 
#   return in error state otherwise SUCCESS
#   - input: 
#   $1 - log file name to be output to.
#   Return:
#   SUCCESS(0) - if currpid.log PID number matches the nvidia-smi output.
#   EXIT_ERR(-1) - for any error condition including the PID stored in currpid.log is not match.

checkRunningMiner()
{
    CURRPID=`cat $MINER_ROOT_DIR/log/currpid.log`
    printColor "ligreen" "checkRunningMiner: currpid: $CURRPID" $1
    CURRPIDTEST=`cat $NVIDIA_SMI_LOG | grep $CURRPID | wc -l`
    printColor "ligreen" "checkRunningMiner: No. of lines matching PID: $CURRPIDTEST" $1

    if [[ -z $CURRPIDTEST ]] || [[ $CURRPIDTEST -eq 0 ]] 
    then
        printColor "red" "checkRunningMiner: No. of matching PID $CURRPID in nvidia-smi is zero. Miner process might have failed." $1
        STAT=1
        return
    fi

    STAT=0
    printColor "ligreen" "checkRunningMiner: CurrPID $CURRPID matches the nvidia-smi output, OK."

}

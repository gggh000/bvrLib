#   The gpu-efficiency profiler is a python script that runs the specific miner for a range of power
#   and determines the GPU mining hash efficieny over that range of power band.
#   The final result is published in a csv format.

#   1.  Construct the csv output format that are ready to use.
#       - Name should signify - model of GPU, miner used, crypto coin and operating system used, as such, 
#       it could take following format: <GPU-MODEL>-<MINER>-<CRYPTOCOIN>-<O.S>.csv.
#       For example, if the efficiency profiler ran on a GPU model GTX1080-FoundersEdition, with EWBF miner
#       to mine zcash on linux: gtx11080fe-ewbf-zcash-lin.csv. Whether it automatically construct the name 
#       user constructs is up for a debate. The certain part of naming might be unavoidably constructed by the 
#       user. For example, nvidia-smi utility does not distinguish (at least to my knowledge up to this point)
#       the model of the GPU card between GTX1080 FE and GTX1080 ROG version. If this can be determined from 
#       somewhere else, the whole output naming can possibly be automatically constructed which is the 
#       preferred option.  
#   
#   2.  Determine the min and max range of power (ideally from nvidia-smi utility). Typically for GTX1080, it is 
#       90-180W however other ranges are possibility. 

#   3.  Ran a series of test over the range in the pre-determined increments. The minimum granularity is ideally
#       10W increments as this generates a easier comparable data. 
#
#   4.  Generate the data using the data collected over range of power. At the minimum data should contain:
#       mandatory:  for specific power: hash/w (average), temperature (average)
#       optional:   for specific power: hash/sec, wattage.
#       
#   Configurable parameters for this script should be:

#   Increment in watts for testing over range of power:

    CONFIG_POWER_RANGE_INCREMENT = 10

#   Duration of test long enough to take accurate average data for give power.

    CONFIG_EFF_TEST_DURATION = 5 

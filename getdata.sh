#!/bin/bash

#tshark -n -r bsm_20170405_0001.pcapng tcp.stream eq 6  -z follow,tcp,raw,6 -w test
MIN_FLOW_NUMBER=1
MAX_FLOW_NUMBER=200
FILE_COUNT=0

for INPUT_FILENAME in "$@"
do
    FILE_COUNT=$(( FILE_COUNT + 1 ))
    seq ${MIN_FLOW_NUMBER} ${MAX_FLOW_NUMBER} | while read i
    do
        echo -n "processing stream ${i} ... "
        STREAM=$(tshark -n -r ${INPUT_FILENAME} tcp.stream eq ${i}) 
        NLINE=$(echo -n "${STREAM}" | wc -l)
        if [ ${NLINE} -eq 0 ]; then
            break
        fi
    
        echo "${STREAM}" | awk '{print $6}' | egrep -q "HTTP|SSL|TLS"
        if [ $? -ne 0 ]; then
            echo "saving"
            tshark -n -r ${INPUT_FILENAME} tcp.stream eq ${i} -z follow,tcp,raw,${i} -w /dev/null > flow_${FILE_COUNT}_${i}
        else
            echo "skip"
        fi
    done
done

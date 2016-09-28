#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --pipeline_name PIPELINE_NAME [ --wait_span WAIT_SPAN --wait_interval WAIT_INTERVAL | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_WAIT_SPAN=100
_WAIT_INTERVAL=10

while [ "$1" != "" ]; do
	case $1 in
		--pipeline_name)    shift
                            _PIPELINE_NAME=$1
                            ;;
		--wait_span)        shift
                            _WAIT_SPAN=$1
                            ;;
		--wait_interval)    shift
                            _WAIT_INTERVAL=$1
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [ -z "$_PIPELINE_NAME" ]; then
	usage;
	exit 1;
fi

jobid=`pachctl list-job -p $_PIPELINE_NAME |grep running |awk '{print $1}'`

while [ -z "$jobid" ] && [ $_WAIT_SPAN -gt 1 ];do
	sleep $_WAIT_INTERVAL
	jobid=`pachctl list-job -p $_PIPELINE_NAME |grep running |awk '{print $1}'`
	_WAIT_SPAN=`echo $(($_WAIT_SPAN-$_WAIT_INTERVAL))`
	echo "continue to wait for $_WAIT_SPAN seconds"
done

if [ ! -z "$jobid" ]; then
	echo "waiting for job $jobid to finish"
	pachctl inspect-job $jobid --block
	echo "job $jobid has finished"
fi

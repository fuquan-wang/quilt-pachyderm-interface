#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO [ [--number_of_tops TOPS] | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_TOPS="10"
while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--number_of_tops)   shift
                            _TOPS=$1
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [ -z "$_INPUT_REPO" ]; then
	usage;
	exit 1;
fi

cat /pfs/$_INPUT_REPO/* > tmpInput;
python quilt-topK.py --input_file tmpInput --output_file tmpOutput --number_of_tops $_TOPS

mv tmpOutput /pfs/out/data

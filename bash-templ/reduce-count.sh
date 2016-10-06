#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO [ [--integer_score] | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_INTEGER="0"
while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--integer_score)    _INTEGER="1"
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
python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number 0 --score_column 1 --integer_score $_INTEGER 

mv tmpOutput /pfs/out/data

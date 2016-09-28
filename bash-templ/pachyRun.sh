#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --executable EXECUTABLE [ [--uuid_filename] | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--executable )      shift
                            _EXECUTABLE=$1
                            ;;
		--uuid_filename)    _UUID_FILENAME="1"
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [ -z "$_INPUT_REPO" ] || [ -z "$_EXECUTABLE" ]; then
	usage;
	exit 1;
fi

for file in `ls /pfs/$_INPUT_REPO/*`; do
	echo "processing file $file";

	cp $file tmpInput;
	[ -f tmpOutput ] && rm -f tmpOutput;
	. $_EXECUTABLE tmpInput tmpOutput;

	if [ "$_UUID_FILENAME"=="1" ]; then
		cp tmpOutput /pfs/out/`uuidgen`;
	else
		cp tmpOutput /pfs/out/`basename $file`;
	fi

done

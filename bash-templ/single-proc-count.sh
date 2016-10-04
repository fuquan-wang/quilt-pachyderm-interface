#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --column_number COLUMN [ [--score_column SCORE --to_lower] | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_SCORE=""
_LOWER="0"
while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--column_number )   shift
                            _COLUMN=$1
                            ;;
		--score_column)     shift
                            _SCORE=$1
                            ;;
		--to_lower)         _LOWER="1"
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [ -z "$_INPUT_REPO" ] || [ -z "$_COLUMN" ]; then
	usage;
	exit 1;
fi

mkdir /pachy-out
for file in `ls /pfs/$_INPUT_REPO/*`; do
	echo "processing file $file";

	cp $file tmpInput
	[ -f tmpOutput ] && rm -f tmpOutput;
	if [ -z "$_SCORE" ]; then
		if [ "$_LOWER" -eq "1" ]; then 
			python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number $_COLUMN --to_lower 1 --integer_score 1
		else
			python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number $_COLUMN --integer_score 1
		fi
	else
		if [ "$_LOWER" -eq "1" ]; then 
			python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number $_COLUMN --to_lower 1 --score_column $_SCORE --integer_score 0
		else
			python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number $_COLUMN --score_column $_SCORE --integer_score 0
		fi
	fi

	mv tmpOutput /pachy-out/`basename $file`
done

cat /pachy-out/* > tmpInput
if [ -z "$_SCORE" ]; then
	python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number 0 --score_column 1 --integer_score 1
else
	python quilt-count.py --input_file tmpInput --output_file tmpOutput --column_number 0 --score_column 1 --integer_score 0
fi

mv tmpOutpt /pfs/out/`uuidgen`

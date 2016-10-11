#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --parallelism PARALLELISM --column_number COLUMN --output_file OUTPUT_FILE [ [--score_column SCORE --to_lower TOLOWER --integer_score ISINTEGER] | [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_SCORE=""
_LOWER="0"
_ISINTEGER="0"
while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--parallelism)      shift
                            _PARALLELISM=$1
                            ;;
		--column_number )   shift
                            _COLUMN=$1
                            ;;
		--score_column)     shift
                            _SCORE=$1
                            ;;
		--to_lower)         shift
                            _LOWER=$1
                            ;;
		--integer_score)    shift
                            _ISINTEGER=$1
                            ;;
		--output_file)      shift
                            _OUTPUT_FILE=$1
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [ -z "$_INPUT_REPO" ] || [ -z "$_PARALLELISM" ] || [ -z "$_OUTPUT_FILE" ] || [ -z "$_COLUMN" ]; then
	usage;
	exit 1;
fi

[ -f $_OUTPUT_FILE ] && rm -rf $_OUTPUT_FILE
(
cat << EOF
{
	"pipeline": {
		"name": "COUNT_STEP1_$_INPUT_REPO"
	},
	"transform": {
		"cmd": [ "sh" ],
		"stdin": [
EOF
) >> $_OUTPUT_FILE
if [ -z "$_SCORE" ]; then
	if [ "$_LOWER" == "0" ]; then
		echo -e "\t\t\t\"/single-proc-count.sh --input_repo $_INPUT_REPO --column_number $_COLUMN\"" >> $_OUTPUT_FILE;
	else
		echo -e "\t\t\t\"/single-proc-count.sh --input_repo $_INPUT_REPO --column_number $_COLUMN --to_lower\"" >> $_OUTPUT_FILE;
	fi
else
	if [ "$_LOWER" == "0" ]; then
		echo -e "\t\t\t\"/single-proc-count.sh --input_repo $_INPUT_REPO --column_number $_COLUMN --score_column $_SCORE\"" >> $_OUTPUT_FILE;
	else
		echo -e "\t\t\t\"/single-proc-count.sh --input_repo $_INPUT_REPO --column_number $_COLUMN --to_lower --score_column $_SCORE\"" >> $_OUTPUT_FILE;
	fi
fi
(
cat << EOF
		 ],
		"image": "fuquanwang/count-and-topk:latest"
	},
	"parallelism_spec": {
		"strategy": "CONSTANT",
		"constant": $_PARALLELISM
	},
	"inputs": [
	{
		"repo": {
			"name": "$_INPUT_REPO"
		}
	}
	]
}
{
	"pipeline": {
		"name": "COUNT_$_INPUT_REPO"
	},
	"transform": {
		"cmd": [ "sh" ],
		"stdin": [
EOF
) >> $_OUTPUT_FILE
if [ "$_ISINTEGER" == "0" ]; then
	echo -e "\t\t\t\"/reduce-count.sh --input_repo COUNT_STEP1_$_INPUT_REPO\"" >> $_OUTPUT_FILE;
else
	echo -e "\t\t\t\"/reduce-count.sh --input_repo COUNT_STEP1_$_INPUT_REPO --integer_score\"" >> $_OUTPUT_FILE;
fi
(
cat << EOF
		 ],
		"image": "fuquanwang/count-and-topk:latest"
	},
	"parallelism_spec": {
		"strategy": "CONSTANT",
		"constant": 1
	},
	"inputs": [
	{
		"repo": {
			"name": "COUNT_STEP1_$_INPUT_REPO"
		}
	}
	]
}
EOF
) >> $_OUTPUT_FILE

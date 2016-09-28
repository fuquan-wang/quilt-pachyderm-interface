#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --output_repo OUTPUT_REPO --output_file OUTPUT_FILE <--nlines NLINES --splitter>|--merger | [ [--help | -h] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_SPLITTER="0" 
_MERGER="0"

while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--output_repo)      shift
                            _OUTPUT_REPO=$1
                            ;;
		--output_file)      shift
                            _OUTPUT_FILE=$1
                            ;;
		--nlines)           shift
                            _NLINES=$1
                            ;;
		--splitter)         _SPLITTER="1"
                            ;;
		--merger)           _MERGER="1"
                            ;;
		-h | --help )       usage
                            exit
                            ;;
		* )                 usage
                            exit 1
	esac
	shift
done

if [[ "$_SPLITTER" -eq "0" ]] && [[ "$_MERGER" -eq "0" ]]; then
	usage;
	exit 1;
fi

if [[ "$_SPLITTER" -eq "1" ]] && [[ "$_MERGER" -eq "1" ]]; then
	usage;
	exit 1;
fi

if [ -z "$_INPUT_REPO" ] || [ -z "$_OUTPUT_REPO" ] || [ -z "$_OUTPUT_FILE" ]; then
	usage;
	exit 1;
fi

if [[ "$_SPLITTER" -eq "1" ]] && [[ -z "$_NLINES" ]]; then
	usage;
	exit 1;
fi

[ -f $_OUTPUT_FILE ] && rm -f $_OUTPUT_FILE;


[ -f $_OUTPUT_FILE ] && rm -rf $_OUTPUT_FILE
(
cat << EOF
{
	"pipeline": {
		"name": "$_OUTPUT_REPO"
	},
	"transform": {
		"cmd": [ "sh" ],
		"stdin": [
EOF
) >> $_OUTPUT_FILE

if [[ "$_SPLITTER" -eq "1" ]]; then
	echo -e "\t\t\t\"split -d -a 10 -l $_NLINES /pfs/$_INPUT_REPO/data /pfs/out/data_\"" >> $_OUTPUT_FILE;
else
	echo -e "\t\t\t\"for i in `/pfs/$_INPUT_REPO/*`; do cat /pfs/$_INPUT_REPO/$i >> /pfs/out/data; done\"" >> $_OUTPUT_FILE;
fi

(
cat << EOF
		],
		"image": "fuquanwang/pach-job-shim:latest"
	},
	"parallelism_spec": {
		"strategy": "CONSTANT",
		"constant": 1
	},
	"inputs": [
		{
			"repo": {
				"name": "$_INPUT_REPO"
			}
		}
	]
}
EOF
) >> $_OUTPUT_FILE

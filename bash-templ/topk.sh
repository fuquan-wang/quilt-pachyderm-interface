#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --output_file OUTPUT_FILE [ [--number_of_tops TOPS] | [--help | -h] ]\n"
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

if [ -z "$_INPUT_REPO" ] || [ -z "$_OUTPUT_FILE" ]; then
	usage;
	exit 1;
fi

[ -f $_OUTPUT_FILE ] && rm -rf $_OUTPUT_FILE
(
cat << EOF
{
	"pipeline": {
		"name": "TOPK_$_INPUT_REPO"
	},
	"transform": {
		"cmd": [ "sh" ],
		"stdin": [
					"/reduce-topK.sh --input_repo $_INPUT_REPO --number_of_tops $_TOPS"
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
			"name": "$_INPUT_REPO"
		}
	}
	]
}
EOF
) >> $_OUTPUT_FILE

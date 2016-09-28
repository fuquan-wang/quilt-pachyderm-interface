#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --input_repo INPUT_REPO --parallelism PARALLELISM --docker_user DOCKER_USER --docker_image DOCKER_IMAGE --pipeline_name PIPELINE_NAME
		--output_file OUTPUT_FILE | [ --docker_version DOCKER_VERSION | [--help | -h ] ]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

_DOCKER_VERSION="latest"
while [ "$1" != "" ]; do
	case $1 in
		--input_repo)       shift
                            _INPUT_REPO=$1
                            ;;
		--parallelism)      shift
                            _PARALLELISM=$1
                            ;;
		--docker_user)      shift
                            _DOCKER_USER=$1
                            ;;
		--docker_image)     shift
                            _DOCKER_IMAGE=$1
                            ;;
		--docker_version)   shift
                            _DOCKER_VERSION=$1
                            ;;
		--pipeline_name)    shift
                            _PIPELINE_NAME=$1
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

if [ -z "$_INPUT_REPO" ] || [ -z "$_PARALLELISM" ] || [ -z "$_DOCKER_USER" ] || [ -z "$_DOCKER_IMAGE" ] || [ -z "$_OUTPUT_FILE" ] || [ -z "$_PIPELINE_NAME" ]; then
	usage;
	exit 1;
fi


[ -f $_OUTPUT_FILE ] && rm -rf $_OUTPUT_FILE
(
cat << EOF
{
	"pipeline": {
		"name": "$_PIPELINE_NAME"
	},
	"transform": {
		"cmd": [ "sh" ],
		"stdin": [
			"/pachyRun.sh $_INPUT_REPO"
		],
		"image": "$_DOCKER_USER/$_DOCKER_IMAGE:$_DOCKER_VERSION"
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
EOF
) >> $_OUTPUT_FILE

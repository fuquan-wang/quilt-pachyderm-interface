#!/bin/bash

function usage
{
	    echo -e "\nusage: $0 --tar_ball TAR_BALL --script SCRIPT --workdir WORKDIR --output_file OUTPUT_FILE | [--help | -h]\n"
}

#### Main

if [ $# -lt 1 ]; then
	usage;
	exit 1;
fi

while [ "$1" != "" ]; do
	case $1 in
		--tar_ball)         shift
                            _TAR_BALL=$1
                            ;;
		--script)           shift
                            _SCRIPT=$1
                            ;;
		--workdir)          shift
                            _WORKDIR=$1
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

if [ -z "$_TAR_BALL" ] || [ -z "$_SCRIPT" ] || [ -z "$_WORKDIR" ] || [ -z "$_OUTPUT_FILE" ]; then
	usage;
	exit 1;
fi
_TAR_BALL=`basename $_TAR_BALL`
_SCRIPT=`basename $_SCRIPT`

[ -f $_OUTPUT_FILE ] && rm -rf $_OUTPUT_FILE
(
cat << EOF
FROM fuquanwang/pach-job-shim:latest

# UPDATE reop
RUN apt-get update

# ADD pip package list
ADD requirements.txt /

# Install pip libraries
RUN pip install -U pip setuptools && \
pip install -r /requirements.txt

# Extract the package
ADD $_TAR_BALL /

# ADD script
ADD pachyRun.sh /
RUN chmod 777 /pachyRun.sh

# SET workdir
WORKDIR /$_WORKDIR
EOF
) >> $_OUTPUT_FILE

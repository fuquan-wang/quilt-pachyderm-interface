#!/bin/bash

if [ $# != 1 ];
then
	echo "Usage: $0 <INPUTREPO>";
	exit;
fi

INPUTREPO=$1

for file in `ls /pfs/$INPUTREPO/*`; do 
	sh runLocal.sh $file /pfs/out/`uuidgen`;
done

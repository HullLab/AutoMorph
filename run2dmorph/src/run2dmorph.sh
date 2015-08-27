#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage: run2dmorph <control file>"
	exit
fi

CONTROLFILE=`readlink -f $1`

matlab -nodisplay -nodesktop -nosplash -r "addpath('/hull-disk1/ph269/software/run2dmorph/current'); run2dmorph('$CONTROLFILE'); exit"

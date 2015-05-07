#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Usage: run2dmorph <control file>"
	exit
fi

CONTROLFILE=`$PWD $1`
export PATH=$PATH:/Applications/MATLAB_R2014a.app/bin

matlab -nodisplay -nodesktop -nosplash -r "run2dmorph('$CONTROLFILE'); exit"

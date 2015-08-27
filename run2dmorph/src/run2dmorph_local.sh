#!/bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: run2dmorph_local <path to run2dmorph software> <control file>"
	exit
fi

matlab -nodisplay -nodesktop -nosplash -r "addpath('$1'); run2dmorph('$2'); exit"

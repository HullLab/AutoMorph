#!/bin/bash

PWD=`dirname $0`
export U3D_LIBDIR="$PWD/lib"
"$PWD/IDTFConverter" $@

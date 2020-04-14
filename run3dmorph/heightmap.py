#!/usr/bin/python

import os
import textwrap
import glob
import struct
import platform
import subprocess
import time


def writeMacro(settings,obj):
    '''
    Writes macro for FIJI to generate heightmap from z-stack images.
    '''
    with open(obj.macro,'wb') as f:
        if settings['macro']:
            stackReg = '\nrun("StackReg ", "transformation=[Scaled Rotation]");'
        else:
            stackReg = ''

        macroText = textwrap.dedent("""\
                    setBatchMode(true);
                    run("Image Sequence...", "open={0} file=[{1}] convert sort");{2}
                    run("Stack Focuser ", "enter={3} generate");
                    selectWindow("Focused_{4}");
                    saveAs("Tiff","{5}");
                    selectWindow("HeightMap_{6}");
                    saveAs("Tiff","{7}");
                    selectWindow("{8}");
                    close("*");
                    """)

        zStackDir = obj.stack
        imageExt = obj.stackExt
        kernelHM = settings['kernel_heightmap']
        tempWindow = obj.name.split('.')[0]
        focusedFileName = obj.fijiFocused
        heightmapFileName = obj.heightmap
        objectWindow = obj.name

        toWrite = macroText.format(zStackDir,imageExt,stackReg,kernelHM,tempWindow,focusedFileName,tempWindow,heightmapFileName,objectWindow)
        f.write(toWrite)


def checkSystem():
    '''
    Checks system type (Mac OSX, Linux, or Windows) and architecture (32 or 64
    bit) for specifying FIJI exectuable call.
    '''
    system = platform.system()
    architecture = struct.calcsize('P') * 8
    return system,architecture


def runFIJI(settings,obj):
    '''
    Runs FIJI with written macro file.
    '''
    system,architecture = checkSystem()
    sysDict = {'Darwin':'macosx','Linux':'linux'+str(architecture)}
    fijiCall = ' '.join(['-'.join(['ImageJ',sysDict[system]]),'--headless','--memory=1000m','-macro',obj.macro])
    # Suppress call output by redirecting output to DEVNULL
    FNULL = open(os.devnull,'w')
    subprocess.call(fijiCall,shell=True,stdout=FNULL,stderr=subprocess.STDOUT)


def makeHeightMap(settings,obj):
    '''
    Wrapper function for height map generation.
    '''
    # Start timer on object processing
    start = time.time()
    # Write FIJI macro, run FIJI on object, and save checkpoint
    writeMacro(settings,obj)
    runFIJI(settings,obj)
    # End timer
    end = time.time()
    time_elapsed = end - start
    print '\tINFO: Time elapsed: {:.3f} seconds\n'.format(time_elapsed)

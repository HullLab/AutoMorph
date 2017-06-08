#!/usr/bin/python

import os
import sys


def checkRestart(cpFile,allObjects):
    '''
    Checks whether a checkpoint file exists in the specified output
    directory; if so, determines what the last completed object was.
    '''
    if os.path.exists(cpFile):
        with open(cpFile,'rU') as f:
            if f.read().strip() == 'complete':
                print 'INFO: All objects in input directory have already been processed. Exiting...\n'
                sys.exit(0)
            else:
                lastObj = int(f.read().strip())
                restart = True
    else:
        restart = False
        lastObj = None

    return restart,lastObj


def setRestartObjects(lastObj,allObjects):
    '''
    Returns list of remaining objects to process if checkpoint file
    exists.
    '''
    objectsLeft = [obj for obj in allObjects if obj.num > lastObj]
    return objectsLeft


def saveCheckpoint(obj,cpFile):
    '''
    Saves checkpoint text file with index of last completed object.
    '''
    if obj.num < obj.total:
        # Save number of last finished object to file
        with open(cpFile,'wb') as f:
            f.write(str(obj.num))
    # If object is last object, update checkpoint file with 'complete' flag
    elif obj.num == obj.total:
        with open(cpFile,'wb') as f:
            f.write('complete')

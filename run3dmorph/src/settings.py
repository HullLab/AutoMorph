#!/usr/bin/python
"""
settings.py

Builds hash map (dictionary) for variable values using control file settings.
"""


def getSettings(controlFile):
    """
    controlFile: path to 3Dmorph control file
    """

    # Read in control file to get variable values
    cFile = open(controlFile,'r')
    lines = cFile.readlines()
    
    # Initialize and build hash map for variable settings
    settings = {}
    for line in lines:
        if '#' in line or line == '\n':
            continue
        else:
            var = line.split('=')[0].strip()
            value = line.split('=')[1].strip()
            settings[var] = value
            
    return settings
    

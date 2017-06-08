#!/usr/bin/python
"""
batchIJSF.py

Script for batch focusing of segment output using StackFocuser
plugin for ImageJ. Generates grayscale focused image and heightmap
for all objects.

Requires an installation of FIJI (http://fiji.sc/Fiji) that is
accessible from the path via the following commands:

    Mac:    'ImageJ-macosx'
    Linux:  'ImageJ-linux32' OR 'ImageJ-linux64'
    
This program will overwrite existing files from previous runs, so
please be careful!

(NOTE: AT THE MOMENT, THIS ONLY WORKS FOR LINUX/TIDE!)
"""

def runIJSF(objDirs,focusedPath,sfPath,kernelSize,macroMode,fijiArchitecture):
    """
    focusedPath: full path to the folder containing the output from
    the AutoMorph 'focus' software.

    sfPath: full path to the 'stackfocused' folder, into which files
    will be outputted

    kernelSize: an odd integer specifying kernel size for heightmap
    generation in StackFocuser.

    fijiArchitecture: an integer in [32,64] that specifies the
    architecture of the installed version of FIJI (default value
    is 32; may be left alone if using MacOSX).
    """

    import glob
    import os
    import shutil
    import platform
    import subprocess
    import time

    # Move to 'stripped' directory within 'focus' directory
    strippedDir = os.path.join(focusedPath,'final/stripped')
    os.chdir(strippedDir)
    
    # Check image extension type
    temp = glob.glob(os.path.join(objDirs[0],'*'))
    temp_ext = [os.path.splitext(x)[-1] for x in temp]
    ext = max(set(temp_ext),key=temp_ext.count)

    # Loop through object directories and run ImageJ StackFocuser
    print 'Begin FIJI processing...\n'
    for obj in objDirs:
    	start = time.time()
        print 'Object: ' + obj
        imageStackDir = os.path.join(strippedDir,obj)
        pathToMacroFile = writeIJMacro(imageStackDir,sfPath,obj,kernelSize,macroMode,ext)
        # Move 'ZS.tif' file to separate folder
        zsPath = os.path.join(imageStackDir,'ZS')
        if not os.path.exists(zsPath):
            os.mkdir(zsPath)
            zsFile = os.path.join(imageStackDir,'ZS.tif')
            if os.path.exists(zsFile):
            	shutil.move(zsFile,zsPath)
            else:
            	continue
            
        # Determine and set system and architecture
        sysPlatform = platform.system()
        if sysPlatform == 'Linux':
            if fijiArchitecture == '32':
                sysarchSpecifier = 'linux32'
            elif fijiArchitecture == '64':
                sysarchSpecifier = 'linux64'
            else:
                raise ValueError('FIJI architecture inappropriately specified (must be 32 or 64)')
        elif sysPlatform == 'Darwin':
            sysarchSpecifier = 'macosx'
        else:
            raise ValueError('Inappropriate system (must be Linux or Darwin)')

        # Build final command text
        ijCommand = 'ImageJ-' + sysarchSpecifier + ' --headless --memory=5000m -macro ' + pathToMacroFile
        # Call FIJI command externally
        subprocess.call(ijCommand,shell=True)
        end = time.time()
        time_elapsed = end - start
	print 'Time Elapsed: ' + '%6.3f' % time_elapsed + ' seconds\n'
	

def writeIJMacro(imageStackDir,outputDir,objName,kernelSize,macroMode,ext):
    """
    imageStackDir: full path to folder containing stack of images for
    an object

    outputDir: full path to output directory for macro files

    objName: string dictating object name (used as base for file name
    for macro file)

    kernelSize: an odd integer specifying kernel size for heightmap
    generation in StackFocuser.
    """
    import os

    # Make output folder for object and move to that folder
    objOutputDir = os.path.join(outputDir,objName)
    if not os.path.exists(objOutputDir):
        os.mkdir(objOutputDir)
    os.chdir(objOutputDir)

    # Write individual macro file for object
    macroFilePath = os.path.join(objOutputDir,objName + '_macro.imj')
    macroFile = open(macroFilePath,'wb')
    if macroMode.lower() == 'false':
        macroText = """setBatchMode(true);
run("Image Sequence...", "open={0} file=[{1}] convert sort");
run("Stack Focuser ", "enter={2} generate");
selectWindow("Focused_{3}");
saveAs("Tiff","{4}");
selectWindow("HeightMap_{3}");
saveAs("Tiff","{5}");
selectWindow("{6}");
close("*");
"""
    else:
        macroText = """setBatchMode(true);
run("Image Sequence...", "open={0} file=[{1}] convert sort");
run("StackReg", "transformation=[Scaled Rotation]");
run("Stack Focuser ", "enter={2} generate");
selectWindow("Focused_{3}");
saveAs("Tiff","{4}");
selectWindow("HeightMap_{3}");
saveAs("Tiff","{5}");
selectWindow("{6}");
close("*");
"""
    var0 = imageStackDir
    var1 = str(ext)
    var2 = kernelSize
    var3 = objName.split('.')[0]
    var4 = os.path.join(objOutputDir,objName+'_focused.tif')
    var5 = os.path.join(objOutputDir,objName+'_heightmap.tif')
    var6 = objName
    textToWrite = macroText.format(var0,var1,var2,var3,var4,var5,var6)

    macroFile.write(textToWrite)
    macroFile.close()

    return macroFilePath    

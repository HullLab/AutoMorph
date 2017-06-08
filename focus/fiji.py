"""
fiji.py

Adapted from batchIJSF.py

Script for batch focusing of segment output using StackFocuser
plugin for FIJI. Generates grayscale focused image and heightmap
for all objects.

Requires an installation of FIJI (http://fiji.sc/Fiji) that is
accessible from the path via the following commands:

    Mac:    'ImageJ-macosx'
    Linux:  'ImageJ-linux32' OR 'ImageJ-linux64'

This program will overwrite existing files from previous runs, so
please be careful!

(NOTE: AT THE MOMENT, THIS ONLY WORKS FOR LINUX/TIDE!)
"""

import os
import glob
import time
import platform
import subprocess


def run(directories, software):
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

    # os.chdir(directories['stripped'])

    system_platform = platform.system()

    if system_platform == 'Linux':
        if software['fiji_architecture'] == '32':
            architecture = 'linux32'
        elif software['fiji_architecture'] == '64':
            architecture = 'linux64'
        else:
            raise ValueError('FIJI architecture inappropriately specified (must be 32 or 64)')
    elif system_platform == 'Darwin':
        architecture = 'macosx'
    else:
        raise ValueError('Inappropriate system (must be Linux or Darwin)')

    stripped_objects = [os.path.realpath(x) for x in glob.glob(os.path.join(directories["stripped"],
                                                                            '*_obj*'))]

    print 'Begin FIJI processing...\n'

    command = 'ImageJ-' + architecture + ' --headless --memory=1000m -macro '

    for stripped_object in stripped_objects:
        start = time.time()
        print 'Object: ' + stripped_object

        batch_file = write_batchfile(stripped_object, directories, software)

        subprocess.call(command+batch_file, shell=True)

        end = time.time()
        time_elapsed = end - start
        print 'Time Elapsed: ' + '%6.3f' % time_elapsed + ' seconds\n'

    # check
    first_object = os.path.realpath(os.path.join(directories['stripped'],
                                                 os.path.basename(directories["objects"][0]),
                                                 'ij_focused.tif'))
    last_object = os.path.realpath(os.path.join(directories['stripped'],
                                                os.path.basename(directories["objects"][-1]),
                                                'ij_focused.tif'))

    if not os.path.exists(first_object):
        sys.exit("Error: FIJI didn't create files. Perhaps something went wrong? Exiting...")
    elif not os.path.exists(last_object):
        sys.exit("Error: FIJI didn't finish creating files. Perhaps something went wrong? Exiting...")
    else:
        print 'FIJI finished!'


def write_batchfile(stripped_object, directories, software):
    """
    imageStackDir: full path to folder containing stack of images for
    an object

    outputDir: full path to output directory for macro files

    objName: string dictating object name (used as base for file name
    for macro file)

    kernelSize: an odd integer specifying kernel size for heightmap
    generation in StackFocuser.
    """

    obj_name = os.path.basename(stripped_object)

    # Determine image extension by counting most common image extension in
    # target object folder
    objects = glob.glob(os.path.join(stripped_object,'*'))
    extensions = [os.path.splitext(obj)[1] for obj in objects]
    extension = max(extensions,key=extensions.count)

    # Write individual macro file for object
    macro_file_path = os.path.join(stripped_object,'macro.imj')
    macro_file = open(macro_file_path,'w')
    macro_text = """setBatchMode(true);
run("Image Sequence...", "open={0} file=[{1}] convert sort");
run("Stack Focuser ", "enter={2} generate");
selectWindow("Focused_{3}");
saveAs("Tiff","{4}");
selectWindow("HeightMap_{5}");
saveAs("Tiff","{6}");
selectWindow("{7}");
close("*");
"""

    macro_text = macro_text.format(stripped_object,
                                   extension,
                                   software['kernel_size'],
                                   obj_name.split('.')[0],
                                   os.path.join(stripped_object,'ij_focused.tif'),
                                   os.path.join(stripped_object,'ij_heightmap.tif'),
                                   obj_name)

    macro_file.write(macro_text)
    macro_file.close()

    return macro_file_path

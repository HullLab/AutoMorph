#!/usr/bin/python

# iFocus - combine stacks of images into focused one via Helicon software
import sys
import glob
import tempfile
import os
import shutil
import time

# Definitions:
#zerenePath = '/hull-disk
#heliconPath = '/hull-disk1/ph269/software/HeliconFocus/current/drive_c/Program\ Files/Helicon\ Software/Helicon\ Focus\ 6/HeliconFocus.exe'
#heliconOptions = ' -silent -mp:2 -rp:50 -sp:1'

# Grab target directory from command line:
targetDirectory = str(sys.argv[1]) + '/obj*'

# Set up the focused directory:
focusdir = str(sys.argv[1]) + '/focused'
if not os.path.exists(focusdir):
	os.makedirs(focusdir)

# Set up list of target directories:
imageDirectories = glob.glob(targetDirectory)

# Loop over them:
for dir in imageDirectories:

	# Show what directory we're on:
	print 'Focusing ' + dir + ' ...' 

	# Make a temporary directory:  (Currently in /tmp)
	tmpdir = tempfile.mkdtemp(suffix='.convert_temp')

	# Get list of tif files in current directory:
	files = glob.glob(dir + '/*tif')

	# Loop over files:
	for file in files:

		# Get filename and set temporary output file:
		path, filename = os.path.split(file)
		outfile = os.path.join(tmpdir, filename)

		# Strip images of 125-pixel high white space with label:
		convert = 'convert ' + file + ' -crop +0-125 +repage ' + outfile
		os.system(convert)

	# Set up focus and full filename
	path, objectID = os.path.split(dir)
	focusfile = os.path.join(tmpdir, objectID + '.tif')
	fullfile = os.path.join(focusdir, objectID + '.tif')

	# Assemble focused version:
	focus = heliconPath + heliconOptions + ' ' + tmpdir + ' -save:' + focusfile
	os.system(focus)

	# Save label from highest layer:
	labelfile = os.path.join(tmpdir, objectID + '_label.tif')
	getlabel = 'convert ' + files[-1] + ' -gravity South -crop 0x125+0+0 ' + labelfile
	os.system(getlabel)

	# Reattach label:
	reattach = 'convert -append ' + focusfile + ' ' + labelfile + ' ' + fullfile
	os.system(reattach)

	# Remove temp directory
	#shutil.rmtree(tmpdir, ignore_errors=True)

	# Sleep for 1 second before we do the next one:
	time.sleep(1)

# Done
print 'Done!'





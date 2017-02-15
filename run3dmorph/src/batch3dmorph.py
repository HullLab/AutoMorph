#!/usr/bin/python

from settings import *
from batchIJSF import *
from writeLatexFile import *
import os
import shutil
import subprocess
import glob
import sys

version = '2016.10.25'
print 'Run3dmorph Version: ' + version

controlFile = sys.argv[1]
try:
    reset = sys.argv[2]
except:
    reset = 'no-reset'

settings = getSettings(controlFile)

# Set up necessary paths and create 'morph3d' and 'stackfocused' folders to contain output
focusedPath = settings['directory']
run3dmorphPath = settings['path_run3dmorph']
run2dmorphPath = settings['path_run2dmorph']
morph3dPath = os.path.join(settings['output_dir'],'morph3d')

# Restart if specified
if reset == 'reset':
	shutil.rmtree(morph3dPath)

sfPath = os.path.join(morph3dPath,'stackfocused')
if not os.path.exists(morph3dPath):
    os.mkdir(morph3dPath)
if not os.path.exists(sfPath):
    os.mkdir(sfPath)

# Set up variables for running StackFocuser in ImageJ/FIJI
kernelSize = settings['kernel_size_SF']
fijiArchitecture = settings['fiji_architecture']
macroMode = settings['macro_mode']
# Set default values as necessary
if kernelSize == '[]':
    kernelSize = 11
if fijiArchitecture == '[]':
    fijiArchitecture = '32'
elif fijiArchitecture == 'None':
    fijiArchitecture = 0
    
# If restarting, check where to restart (with FIJI or mesh extraction)
totalObjects = [os.path.basename(x) for x in glob.glob(os.path.join(focusedPath,'final','stripped','*obj*'))]
FIJIObjects = [os.path.basename(x) for x in glob.glob(os.path.join(sfPath,'*'))]
OFFObjects = [os.path.basename(x)[:-4] for x in glob.glob(os.path.join(morph3dPath,'off_files','*'))]
if len(FIJIObjects) < len(totalObjects):
	objDirs = list(set(totalObjects) - set(FIJIObjects))
	objDirs.sort()
	runIJSF(objDirs,focusedPath,sfPath,kernelSize,macroMode,fijiArchitecture)
	objDirs = list(totalObjects)
	objDirs.sort()
	skipMeshExtraction = False
else:
	if len(OFFObjects) < len(totalObjects):
		objDirs = list(set(totalObjects) - set(OFFObjects))
		objDirs.sort()
		skipMeshExtraction = False
	else:
		skipMeshExtraction = True

objDirs_all = totalObjects
objDirs_all.sort()
objNamesClean = [''.join(x.split('.')) for x in list(totalObjects)]

# Loop through object folders
if not skipMeshExtraction:
	imgSrcDir = os.path.join(focusedPath,'final/focused_unlabeled')
	imgDstDirBase = os.path.join(morph3dPath,'stackfocused')
	for obj in objDirs:
		print '\nProcessing ' + obj + '...'
		# 1) Copy RGB focused image from 'focused_unlabeled' folder
		# into individual 'stackfocused' object folder
		imgSrcPath = os.path.join(imgSrcDir,obj + '.tif')
		imgDstPath = os.path.join(imgDstDirBase,obj,obj + '_focused_rgb.tif')
		try:
			shutil.copy(imgSrcPath,imgDstPath)
		except:
			skip = True
			continue
		# 2) Run morph3dwrapper.m externally on each object
		fileNameBase = os.path.join(imgDstDirBase,obj,obj)
		focusedImageGrayscale = fileNameBase + '_focused.tif'
		focusedImageRGB = fileNameBase + '_focused_rgb.tif'
		heightmap = fileNameBase + '_heightmap.tif'
		if os.path.exists(heightmap):
			matlabCommand = 'matlab -nodisplay -nodesktop -nosplash -r "addpath(' + '\'' + settings['path_run3dmorph'] + '\'' + '); addpath(' + '\'' + settings['path_run2dmorph'] + '\'' + '); morph3dwrapper(' + '\'' + run3dmorphPath + '\',''' + '\'' + morph3dPath + '\',\'' + focusedImageRGB + '\',\'' + heightmap + '\',\'' + obj + '\',\'' + settings['sampleID'] + '\',' + settings['macro_mode'].lower() + ',\'' + settings['unit'] + '\',' + settings['calibration'] + ',' + settings['num_slices'] + ',' + settings['zstep'] + ',' + settings['kernel_size_OF'] + ',' + settings['downsample_grid_size'] + ',' + settings['savePDF'] + ',' + settings['intensity_range_in'] + ',' + settings['intensity_range_out'] + ',' + settings['gamma'] + ',' + settings['threshold_adjustment'] + ',' + settings['noise_limit'] + '); exit"'
			# Run Matlab and suppress header
			os.system(matlabCommand + '| tail -n +13')
		else:
			print 'Object skipped.'
			continue
	# Cleanup
	#shutil.rmtree(os.path.join(run3dmorphPath,'morph2d'))

# Remaining 3D PDF Steps: 1) Convert IDTF -> U3D; 2) Write LaTeX files; 3) Run LaTeX files
if settings['savePDF'] == 'true' or settings['savePDF'] == '[]':
	print '\nBuilding 3D PDF files...'
	# Build 'pdf_3d', 'u3d_files', and 'idtf_files' folders and paths
	pdf3dPath = os.path.join(morph3dPath,'pdf_3d')
	idtfPath = os.path.join(pdf3dPath,'idtf_files')
	u3dPath = os.path.join(pdf3dPath,'u3d_files')
	if not os.path.exists(u3dPath):
		os.mkdirs(u3dPath)
	if not os.path.exists(idtfPath):
		os.mkdirs(idtfPath)
	# Loop through IDTF files and convert to U3D
	print '\tBuilding U3D files...'
	# Check system architecture for writing IDTF command
	sysArch = sys.platform
	# Write all commands to temp file
	commandFile = open('idtfCommands.txt','w')
	for obj in objNamesClean:
		idtfFilePath = os.path.join(idtfPath,obj + '.idtf')
		u3dFileName = obj + '.u3d'
		u3dOutputFilePath = os.path.join(u3dPath,u3dFileName)
		if 'linux' in sysArch:
		    idtfCommand = ' '.join([os.path.join(run3dmorphPath,'mesh2pdf','bin','glx','IDTFConverter.sh'),' -input',idtfFilePath,'-output',u3dOutputFilePath])
		elif 'darwin' in sysArch:
		    idtfCommand = ' '.join(['cd',os.path.join(run3dmorphPath,'mesh2pdf','bin','maci'),';','./IDTFConverter','-input',idtfFilePath,'-output',u3dOutputFilePath])
		commandFile.write(idtfCommand + ' | tail -n +30\n')
	commandFile.close()
	# Run commands from file
	commandFile = open('idtfCommands.txt','r')
	lines = commandFile.readlines()
	for line in lines:
		os.system(line.strip())
	commandFile.close()
	# Cleanup
	os.remove('idtfCommands.txt')
	# Make 'latex_files' folder if it doesn't exist
	latexOutputPath = os.path.join(pdf3dPath,'latex_files')
	if not os.path.exists(latexOutputPath):
		os.mkdir(latexOutputPath)
	# Loop through U3D files and write LaTeX files
	print '\tBuilding LaTeX files...'
	for obj in objDirs_all:
		u3d = os.path.join(u3dPath,''.join(obj.split('.')) + '.u3d')
		outputFileNameBase = obj
		outputFileName = outputFileNameBase + '.tex'
		outputFilePath = os.path.join(latexOutputPath,outputFileName)
		media9Path = run3dmorphPath
		try:
			writeLatexFile(u3d,media9Path,outputFileNameBase,outputFilePath,focusedPath,sfPath,settings['unit'])
		except:
			print '\t\t' + obj + ': Cannot build LaTeX file.'
			continue
	# Run LaTeX if specified
	if settings['run_latex'] == 'true':
		print '\tRunning LaTeX...'
		pdfsPath = os.path.join(pdf3dPath,'pdfs')
		if not os.path.exists(pdfsPath):
			os.mkdir(pdfsPath)
		os.chdir(latexOutputPath)
		latexFiles = glob.glob('*.tex')
		for latex in latexFiles:
			latexCommand = ' '.join(['pdflatex',latex,'| tail -n +300'])
			os.system(latexCommand)
		pdfFiles = glob.glob('*.pdf')
		print '\nCleaning up...'
		for pdf in pdfFiles:
			shutil.copy(pdf,pdfsPath)
print '\nDone!'
 

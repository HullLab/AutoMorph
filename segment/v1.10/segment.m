% Segment uses the bounding box identified by the sharpest image in a 
% set of stacks to chop just the edf into individual images

%Started on 3/21/2014 by Yusu Liu 
% code uses base code of PM Hull (20-Oct-13)with updates by B. Dobbins, PMH, and Y. Liu
% NOTE: It is now a function, not a stand-alone script
%       (Additional info on the parameters coming soon by brian)
function segment(settingsFile)

% Set version number:
version='2014-09-03a';

% Read in the settings:
settings = parseSettings(settingsFile);

% Main loop over all potential configurations:
for run = 1:length(settings)
	fprintf('iSegment - running configuration %d of %d from %s \n', run, length(settings), settingsFile);
	
	% Get list of images in directory:
	targetImages = imageList(settings(run).directory, settings(run).debug);

	% Get the microns per pixel for this image:	(new, and ugly, modification - Oct. 2014)
	settings(run).micronsPerPixel = micronsPerPixel(targetImages{length(targetImages)});

	% Load, resize and border top-level image:
	currentImage = loadImage(targetImages{length(targetImages)}, settings(run));

	% Identify all objects based on threshold & minimumLight values:
	objects = findObjects(currentImage, settings(run));

	% If we're running in 'sample' or 'save' modes, we've got more to do:
  %if ((settings.mode == 'sample') | (settings.mode == 'save'))
  if strcmpi(settings(run).mode, 'sample') | strcmp(settings(run).mode, 'save')

		% If we're running in 'sample' mode, we only use the last plane:
		%if settings.mode == 'sample'
		if strcmpi(settings(run).mode, 'sample')
			startPlane = length(targetImages);
			endPlane = startPlane;
		else
			startPlane = 1;
			endPlane = length(targetImages)-1;
		end

		% Loop over the planes we're interested in, load an image, then process it:
		for plane = startPlane:endPlane
			currentImage = loadImage(targetImages{plane}, settings(run));

			% Sample mode:
			if strcmpi(settings(run).mode, 'sample')
				sample(currentImage, objects, targetImages{plane}, version, settings(run));
			else % Must be 'save':
			% Save all our objects, including samples for the highest plane:
				saveAll(currentImage, objects, targetImages{plane}, plane, version, settings(run));
			end

		end	% End loop over planes
	end % End if we're running in sample or save modes

	% Save the settings:
	% Get the original (end-level) directory:
	directoryID = strsplit(settings(run).directory, filesep);
	directoryID = directoryID{end};

	% Set up main level directory:
	maindirectory = sprintf('%s%s%s%s', settings(run).output, filesep, directoryID, filesep);

	% Set up subdirectory based on tag and settings:
	if strcmp(settings(run).tag, 'final')
		subdirectory = 'final';
	else
		subdirectory = sprintf('%s_th=%05.4f_size=%04.0fu-%04.0fu', settings(run).tag, settings(run).threshold, settings(run).minimumSize, settings(run).maximumSize);
	end

	% Combine the two:
	fulldirectory = fullfile(maindirectory, subdirectory);

	% Set the 'sourcefile':
	parts = strsplit(targetImages{plane}, filesep);
	sourcefile = fullfile(parts{end-1}, parts{end});

	% Save user and settings:
	fprintf('CALLING SAVESETTINGS - dir is %s\n', fulldirectory);
	saveSettings(settings, fulldirectory);



end % End run over various configurations (runs)

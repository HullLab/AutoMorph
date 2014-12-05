
function saveAll(currentImage, objects, source, plane, version, settings)

% Get the original (end-level) directory:
directoryID = strsplit(settings.directory, filesep);
directoryID = directoryID{end};

% Set up main level directory:
maindirectory = sprintf('%s%s%s%s', settings.output, filesep, directoryID, filesep);

% Set up subdirectory based on tag and settings:
subdirectory = sprintf('%s_th=%05.4f_size=%04.0fu-%04.0fu', settings.tag, settings.threshold, settings.minimumSize, settings.maximumSize);

% Combine the two:
fulldirectory = fullfile(maindirectory, subdirectory);

% Set the 'sourcefile':
parts = strsplit(source, filesep);
sourcefile = fullfile(parts{end-1}, parts{end});


% Make subdirectory:
if ~exist(fulldirectory)
	mkdir(fulldirectory);
end

% Save user and settings:
%saveSettings(settings, fulldirectory);

for index = 1:length(objects)
	% Set up the file name and directory:
	if strcmpi(settings.mode, 'sample')
		directory = fullfile(fulldirectory, 'samples');
		filename=strcat(directoryID, '_', 'sample_', sprintf('%02.0f',index), '.tif');
	else
		directory = fullfile(fulldirectory, strcat('object_', sprintf('%05.0f', index)));
		filename=strcat(directoryID, '_', 'obj', sprintf('%05.0f',index), '_', 'plane', sprintf('%03.0f', (plane-1)), '.tif');
	end

	% Get our top left corner:
	x = int64(objects(index).BoundingBox(1));
	y = int64(objects(index).BoundingBox(2));

	% Get our width and height:
	xsize = int64(objects(index).BoundingBox(3));
	ysize = int64(objects(index).BoundingBox(4));

	% create subimage:
	subImage = currentImage(y:(y+ysize), x:(x+xsize),:);

	% If we're not sampling, set up the info area and background (
	xPct = 100 * double(x) / size(currentImage,2);
	yPct = 100 * double(y) / size(currentImage,1);
	description = sprintf('Object #%05d of %05d ( %d x %d pixels at slide position %05.2f%% x %05.2f%% )\n', index, length(objects), xsize, ysize, xPct, yPct);
	newImage = labelImage(subImage, sourcefile, index, description, xPct, yPct, xsize, ysize, version, settings);

	% Save the image:
	if ~exist(directory)
		mkdir(directory);
	end
	fullpath=fullfile(directory, filename);
	imwrite(newImage, fullpath, 'tif');

end


function sample(image, list, source, version, settings)

% Define the size of the length of the square of our region to save (in microns):
regionSize = 3000; 

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

% Mark the bounding boxes of ALL objects:
for n = 1:length(list)
	X = ceil(list(n).BoundingBox(1));
	Y = ceil(list(n).BoundingBox(2));
	sizeX = ceil(list(n).BoundingBox(3));
	sizeY = ceil(list(n).BoundingBox(4));
	pixelSize = 3;
	redValue = 192;

	% Draw top border:
	image(Y:(Y+pixelSize), X:(X+sizeX), 1) = redValue;

	% Draw bottom border:
	image((Y+sizeY - pixelSize):(Y+sizeY), X:(X+sizeX), 1) = redValue;

	% Draw left border:
	image(Y:(Y+sizeY), X:(X+pixelSize), 1) = redValue;

	% Draw right border:
	image(Y:(Y+sizeY), (X+sizeX-pixelSize):(X+sizeX), 1) = redValue;
end

% Save the entire image:
directory = fullfile(fulldirectory, 'samples');
filename=strcat(directoryID, '_', 'boxes', '.jpg');
fullpath=fullfile(directory, filename);

% Make subdirectory:
if ~exist(directory)
  mkdir(directory);
end

% Save user and settings:
%saveSettings(settings, fulldirectory);

% Save file:
imwrite(image, fullpath, 'jpg', 'Quality', 90.0);

% Make list of five sample images:
picked = zeros(size(list, 1), 1);

picked(closest(image, list, 0.25, 0.25)) = 1;
picked(closest(image, list, 0.75, 0.25)) = 1;
picked(closest(image, list, 0.50, 0.50)) = 1;
picked(closest(image, list, 0.25, 0.75)) = 1;
picked(closest(image, list, 0.75, 0.75)) = 1;

picked = picked > 0;
samples = list(picked);

% Adjust the bounding box if we're close to a border:
imagesizeY = size(image,1);
imagesizeX = size(image,2);


for n = 1:length(samples);
  midY = samples(n).BoundingBox(2) + (0.5*samples(n).BoundingBox(4));
  midX = samples(n).BoundingBox(1) + (0.5*samples(n).BoundingBox(3));

  cornerX = midX - (regionSize / 2);
	if cornerX < 0
		cornerX = 0;
	elseif (cornerX + regionSize) > imagesizeX
		cornerX = imagesizeX - regionSize;
	end

  cornerY = midY - (regionSize / 2);
	if cornerY < 0
		cornerY = 0;
	elseif (cornerY + regionSize) > imagesizeY
		cornerY = imagesizeY - regionSize;
	end

	samples(n).BoundingBox(1) = cornerX;
	samples(n).BoundingBox(2) = cornerY;
	samples(n).BoundingBox(3) = regionSize;
	samples(n).BoundingBox(4) = regionSize;
end


for index = 1:length(samples)
	% Set up the file name and directory:
	filename=strcat(directoryID, '_', 'sample_', sprintf('%02.0f',index), '.tif');

	% Get our top left corner:
	x = int64(samples(index).BoundingBox(1));
	y = int64(samples(index).BoundingBox(2));

	% Get our width and height:
	xsize = int64(samples(index).BoundingBox(3));
	ysize = int64(samples(index).BoundingBox(4));

	% create subimage:
	subImage = image(y:(y+ysize), x:(x+xsize),:);

	% Set up the info area and background:
	xPct = 100 * double(x) / size(image,2);
	yPct = 100 * double(y) / size(image,1);

	% Set up the description, then label the sample image:
	description = sprintf('Sample Window %d of %d ( %d x %d pixels at slide position %05.2f%% x %05.2f%% )\n', index, length(samples), regionSize, regionSize,xPct, yPct);
  newImage = labelImage(subImage, sourcefile, index, description, xPct, yPct, xsize, ysize, version, settings);

	% Save the sample:
	fullpath=fullfile(directory, filename);
	imwrite(newImage, fullpath, 'tif', 'Compression', 'lzw');
end


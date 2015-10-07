
function sample(image, list, source, version, settings)

% Define the size of the length of the square of our region to save (in microns):
regionSize = 3000; 

% Get the original (end-level) directory:
directoryID = strsplit(settings.directory, filesep);
directoryID = directoryID{end};

% Set up main level directory:
maindirectory = sprintf('%s%s%s%s', settings.output, filesep, directoryID, filesep);

% Set up subdirectory based on tag and settings:
if strcmp(settings.tag, 'final')
	subdirectory = 'final';
else
  subdirectory = sprintf('%s_th=%05.4f_size=%04.0fu-%04.0fu', settings.tag, settings.threshold, settings.minimumSize, settings.maximumSize);
end

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

% Create our Unique ID:
underScores = strfind(directoryID, '_');
UniqueID = directoryID(1:underScores(1)-1);

% Save the entire image:
directory = fullfile(fulldirectory, 'samples');
%UniqueID=directoryID(1:9);
%filename=strcat(directoryID, '_', 'boxes', '.jpg');
%filename=strcat(UniqueID, '_', 'boxes', '.jpg');
filename=strcat(UniqueID, '_', 'boxes', '.tif');

% Also save a jpg:
filename2=strcat(UniqueID, '_', 'boxes', '.jpg');

% Jpeg here too:
fullpath=fullfile(directory, filename);
fullpath2=fullfile(directory, filename2);

% Make subdirectory:
if ~exist(directory)
  mkdir(directory);
end

% Save user and settings:
%saveSettings(settings, fulldirectory);

% Save file:
%fprintf('About to try saving file... ');
%fprintf('imwrite(%s, %s, %s, %s, %s \n', image, fullpath, 'jpg', 'Quality', '100');
%imwrite(image, fullpath, 'jpg', 'Quality', 100);
imwrite(image, fullpath, 'tif');
%fprintf('After saving file... ');

% Make list of five sample images:
picked = zeros(size(list, 1), 1);

%picked(closest(image, list, 0.25, 0.25)) = 1;
%picked(closest(image, list, 0.75, 0.25)) = 1;
%picked(closest(image, list, 0.50, 0.50)) = 1;
%picked(closest(image, list, 0.25, 0.75)) = 1;
%picked(closest(image, list, 0.75, 0.75)) = 1;
picked(closest(image, list, 0.25, 0.25)) = picked(closest(image, list, 0.25, 0.25)) + 1;
picked(closest(image, list, 0.75, 0.25)) = picked(closest(image, list, 0.75, 0.25)) + 1;
picked(closest(image, list, 0.50, 0.50)) = picked(closest(image, list, 0.50, 0.50)) + 1;
picked(closest(image, list, 0.25, 0.75)) = picked(closest(image, list, 0.25, 0.75)) + 1;
picked(closest(image, list, 0.75, 0.75)) = picked(closest(image, list, 0.75, 0.75)) + 1;

%fprintf('Picked: %d \n', picked);

redundant = picked > 1;
if sum(redundant) > 0
	fprintf('At least one object is picked twice as a sample image; less than five images will be created.\n');
end

picked = picked > 0;
samples = list(picked);

% Adjust the bounding box if we're close to a border:
imagesizeY = size(image,1);
imagesizeX = size(image,2);


for n = 1:length(samples);
  midY = samples(n).BoundingBox(2) + (0.5*samples(n).BoundingBox(4));
  midX = samples(n).BoundingBox(1) + (0.5*samples(n).BoundingBox(3));

  cornerX = midX - (regionSize / 2);
	if cornerX < 1
		cornerX = 1;
	elseif (cornerX + regionSize) > imagesizeX
		cornerX = imagesizeX - regionSize;
	end

  cornerY = midY - (regionSize / 2);
	if cornerY < 1
		cornerY = 1;
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
	%filename=strcat(directoryID, '_', 'sample_', sprintf('%02.0f',index), '.tif');
	filename=strcat(directoryID, '_', 'sample_', sprintf('%02.0f',index), '.jpg');

	% Get our top left corner:
	x = int64(samples(index).BoundingBox(1));
	y = int64(samples(index).BoundingBox(2));

	% Get our width and height:
	xsize = int64(samples(index).BoundingBox(3));
	ysize = int64(samples(index).BoundingBox(4));

	% create subimage:
	%fprintf('Sample # %d -> Subimage dimensions: %g : %g , %g x %g \n', index, y, y+ysize, x, x+xsize);
	%fprintf('samples(index).BoundingBox(1) = %g \n', samples(index).BoundingBox(1));
	subImage = image(y:(y+ysize), x:(x+xsize),:);

	% Set up the info area and background:
	xPct = 100 * double(x) / size(image,2);
	yPct = 100 * double(y) / size(image,1);

	% Set up the description, then label the sample image:
	description = sprintf('Sample Window %d of %d ( %d x %d pixels at slide position %05.2f%% x %05.2f%% )\n', index, length(samples), regionSize, regionSize,xPct, yPct);
  newImage = labelImage(subImage, sourcefile, index, description, xPct, yPct, xsize, ysize, version, settings);

	% Save the sample:
	fullpath=fullfile(directory, filename);
	%imwrite(newImage, fullpath, 'tif', 'Compression', 'lzw');
	imwrite(newImage, fullpath, 'jpg', 'Quality', 90.0);

end


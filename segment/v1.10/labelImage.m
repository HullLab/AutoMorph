function newImage = labelImage(subImage, filename, objectID, description, locX, locY, sizeX, sizeY, version, settings)

minimumX = 640;

% Pad original image with 10-pixel black border in both directions:
newImage = padarray(subImage, [10 10], 0, 'both');

% If we're less than minimumX in the X direction, pad with black:
if size(newImage, 2) < minimumX
	padX = ceil((minimumX - size(newImage,2)) / 2);
	newImage = padarray(newImage, [0 padX], 0, 'both');
end

% Append to y for text (white!) area:
newImage = padarray(newImage, [160 0], 255, 'post');

% Set up 25 and 100-micron bars:

barInPixels_25 = 25 / settings.micronsPerPixel;
barInPixels_100 = 100 / settings.micronsPerPixel;

height = 2;

midX = size(newImage, 2) / 2;
s100 = int64(midX - (barInPixels_100/2));
e100 = int64(midX + (barInPixels_100/2) - 1);
s25 = int64(midX - (barInPixels_25/2));
e25 = int64(midX + (barInPixels_25/2) - 1);

y100 = int64(size(subImage, 1) + 25);
y25 = y100 + 10;

newImage(y100:y100+height,s100:e100,:) = 0;
newImage(y25:y25+height,s25:e25,:) = 0;

newImage = insertText(newImage, [(e100 + 10) (y100+(height/2))], '100 microns', 'FontSize', 10, 'BoxColor', 'white', 'AnchorPoint', 'LeftCenter', 'BoxOpacity', 0);
newImage = insertText(newImage, [(e25 + 10) (y25+(height/2))], '25 microns', 'FontSize', 10, 'BoxColor', 'white', 'AnchorPoint', 'LeftCenter', 'BoxOpacity', 0);

% Set up Catalog Number (CN):
if strncmp('IP.', filename, 3) == 1
	CN = sprintf('YPM IP %s', filename(4:9));
else
	CN = 'None';
end

% Get dirname and shortfilename:
[dirname, shortfile, fileext] = fileparts(filename);
shortfilename = [ shortfile fileext ];


% Set up text fields:
%currentTime = clock;
%textinfo{1} = description;
%textinfo{2} = sprintf('Threshold of %4.2f and size filter of %d - %d microns\n', settings.threshold, settings.minimumSize, settings.maximumSize);
%textinfo{3} = sprintf('%4.2f microns per pixel | Age and Source:  %s from %s\n', settings.micronsPerPixel, settings.age, settings.source);
%textinfo{4} = sprintf('%s\n', settings.timestamp);
%textinfo{5} = sprintf('Processed at Yale Peabody Museum by the Hull Lab  (Catalog Number: %s)\n', CN);
%textinfo{6} = sprintf('CODE VERSION: %s\n', version);
%textinfo{7} = sprintf('Directory: %s\n', dirname);
%textinfo{8} = sprintf('File: %s\n', shortfilename);

currentTime = clock;
textinfo{1} = description;
textinfo{2} = sprintf('%4.2f microns per pixel | Age and Source:  %s from %s\n', settings.micronsPerPixel, settings.age, settings.source);
textinfo{3} = sprintf('Processed at Yale Peabody Museum by the Hull Lab  (Catalog Number: %s)\n', CN);
textinfo{4} = sprintf('CODE VERSION: %s, PROCESSED ON: %s\n', version, settings.timestamp);
textinfo{5} = sprintf('Threshold of %4.2f and size filter of %d - %d microns\n', settings.threshold, settings.minimumSize, settings.maximumSize);
textinfo{6} = sprintf('Directory: %s\n', dirname);
textinfo{7} = sprintf('File: %s\n', shortfilename);


% Add text:
midPointX = size(newImage, 2) / 2;
startY = y25 + 10;

newImage = insertText(newImage, [midPointX startY], textinfo{1}, 'FontSize', 14, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+20)], textinfo{2}, 'FontSize', 14, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+40)], textinfo{3}, 'FontSize', 14, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+70)], textinfo{4}, 'FontSize', 9, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+85)], textinfo{5}, 'FontSize', 9, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+100)], textinfo{6}, 'FontSize', 9, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');
newImage = insertText(newImage, [midPointX (startY+115)], textinfo{7}, 'FontSize', 9, 'BoxColor', 'white', 'AnchorPoint', 'CenterTop');


end



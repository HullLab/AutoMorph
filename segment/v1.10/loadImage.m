% FUNCTION:  loadImage(file, mX, mY, border, verbose)
%
%   This function loads an image, rescales it based on mx & my, adds a border, and 
%   returns the new image
%   v0.0 - Initial version

function currentImage = loadImage(file, settings)

% Start the timer:
tic;

% Get the dimensions of the image:
imageInfo = imfinfo(file);
mImage = imageInfo(1).Width;
nImage = imageInfo(1).Height;

% Get the microns-per-pixel values:
XMLfile = file;
XMLfile(end-2:end) = 'xml';
text = fileread(XMLfile);
mX = regexp(text, '<MicronsPerPixelX>(.+?)</MicronsPerPixelX>', 'tokens');
mX = str2num(cell2mat(mX{1}));
mY = regexp(text, '<MicronsPerPixelY>(.+?)</MicronsPerPixelY>', 'tokens');
mY = str2num(cell2mat(mY{1}));

% Calculate the new dimensions:
%settings.micronsPerPixel = round(mY * 10) / 10.0;  % Nearest tenth of original factor
scaleFactorY = settings.micronsPerPixel / mY;
scaleFactorX = settings.micronsPerPixel / mY;
%mResized = ceil((1/mX) * nImage);
%nResized = ceil((1/mY) * mImage);
mResized = ceil(scaleFactorX * nImage);
nResized = ceil(scaleFactorY * mImage);

% Preallocate arrays for original and scaled image:
originalImage = zeros(nImage, mImage, 3, 'uint8');
scaledImage = zeros(nResized, mResized, 3, 'uint8');

% Read in original image and time the read:
TIF=Tiff(file, 'r');
TIF.setDirectory(1);
originalImage=TIF.read();
TIF.close();

% Resize the image:
scaledImage = imresize(originalImage, [mResized, nResized]);
clear originalImage;

% Apply border - this function deletes compositing edge effects
borderSize = 0.01;
currentImage = border(scaledImage, borderSize);
clear scaledImage;

% Status update:
elapsed = toc;
debugInfo(sprintf('INFO: loadImage processed %s ( %f seconds) \n', file, elapsed), settings.debug >= 1); % Display this is verbosity >= 1

end

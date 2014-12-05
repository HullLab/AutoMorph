% FUNCTION:  loadImage(file, mX, mY, border, verbose)
%
%   This function loads an image, rescales it based on mx & my, adds a border, and 
%   returns the new image
%   v0.0 - Initial version

function MPP = micronsPerPixel(file)

% Get the microns-per-pixel values:
XMLfile = file;
XMLfile(end-2:end) = 'xml';
text = fileread(XMLfile);
mX = regexp(text, '<MicronsPerPixelX>(.+?)</MicronsPerPixelX>', 'tokens');
mX = str2num(cell2mat(mX{1}));
mY = regexp(text, '<MicronsPerPixelY>(.+?)</MicronsPerPixelY>', 'tokens');
mY = str2num(cell2mat(mY{1}));

% Calculate the new dimensions:

MPP = round(mY * 10) / 10.0;  % Nearest tenth of original factor

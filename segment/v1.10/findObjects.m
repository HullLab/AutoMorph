% FUNCTION: findObjects
% This function takes a directory and returns a list of all TIF images in that
% directory 

%function objects = findObjects(currentImage, threshold, minimumLight, skinnyFactor, boxBuffer, minimumLength, maximumLength, debugLevel)
function objects = findObjects(currentImage, settings)

% RGB -> BW by threshold:
bwImage = im2bw(currentImage, settings.threshold);

% Fill holes (dark pixels surrounded by lighter ones):
bwFill = imfill(bwImage, 'holes');
clear bwImage;

% Find connected objects:
connected = bwconncomp(bwFill);

% Label objects:
allObjects = labelmatrix(connected);

% Create list of bounding boxes & filled areas:
boxList = regionprops(allObjects, 'BoundingBox');
totalObjects = length(boxList);

%%% My Matlab-fu is pretty weak and this isn't elegant.. any pointers how to do it better?
% Extract the size of the bounding box into arrays:
boundingBoxes = [boxList.BoundingBox];
sizeX = boundingBoxes(3:4:end);	% Take every 4th element, starting at 3 (width)
sizeY = boundingBoxes(4:4:end); % Take every 4th element, starting at 4 (height)

% Eleminate all boxed objects with a dimension smaller than the minimum and a huge area:
% True minimum length can be smaller if the minimum length is oriented at a 45-degree angle, so calculate it for vertical / horizontal minimums:
minimumSize = settings.minimumSize / settings.micronsPerPixel;
maximumSize = settings.maximumSize / settings.micronsPerPixel;
minimumSize = sqrt((minimumSize * minimumSize) / 2);
boxList = boxList((sizeX > minimumSize) & (sizeX < maximumSize) & (sizeY > minimumSize) & (sizeY < maximumSize));

% Increase the bounding box size:
% NOTE: Currently using hard-coded 20% rule:
boxList = expandBoundingBox(boxList, 0.20, size(allObjects));

% Debug info:
debugInfo(sprintf('INFO: findObjects -> %d total [ Thresh: %f ] -->  %d valid \n', totalObjects, settings.threshold, length(boxList)), settings.debug >= 1); % Display this is verbosity >= 1

objects = boxList;
end

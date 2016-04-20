function resized_image = resizePixelToMicron(image,calibration)
% Resizes an image by multiplying original height and width by the
% pixel-to-micron calibration factor provided.

size_original_image = size(image);
new_height = ceil(size_original_image(1) * calibration);
new_width = ceil(size_original_image(2) * calibration);
resized_image = imresize(image,[new_height,new_width]);
% FUNCTION: imageList(directory, verbosity)
% This function takes a directory and returns a list of all TIF images in that
% directory 

function files = imageList(directory, verbosity)


files = dir(fullfile(directory, '*.tif'));
files = {files.name};

files = fullfile(directory, files);
numFiles = length(files);

debugInfo(sprintf('INFO: imageList found %d files\n', numFiles), verbosity >= 1); % Display this is verbosity >= 1
end


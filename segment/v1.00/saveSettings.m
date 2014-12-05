
function saveSettings(settings, directory)

% Get the user name - currently only works on Unix, but we can modify in the future
[~, username] = system('whoami');
username = username(1:end-1);	% Remove newline

% Get the date:
timestamp = datestr(now,'yyyy_mm_dd-HH:MM:SS.FFF');

% Construct file name:
filename = sprintf('settings_%s_%s.txt', username, timestamp);

% Open the file:
fileID =  fopen(fullfile(directory, filename), 'w');

% Write to file:
fprintf(fileID, '# Saved Settings:');
fprintf(fileID, 'directory = %s\n', settings.directory);
fprintf(fileID, 'output = %s\n', settings.output);
fprintf(fileID, 'threshold = %05.2f\n', settings.threshold);
fprintf(fileID, 'minimumSize = %f\n', settings.minimumSize);
fprintf(fileID, 'maximumSize = %f\n', settings.maximumSize);
fprintf(fileID, 'mode = %s\n', settings.mode);
fprintf(fileID, 'debug = %d\n', settings.debug);			% Debug needs to be fixed
fprintf(fileID, 'tag = %s\n', settings.tag);
fprintf(fileID, 'source = %s\n', settings.source);
fprintf(fileID, 'age = %s\n', settings.age);
fprintf(fileID, '# micronsPerPixel = %f\n', settings.micronsPerPixel);

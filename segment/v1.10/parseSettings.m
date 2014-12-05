
function settings = parseSettings(filename)

% Specify default values for optional parameters in case options are not set:
tag = '';
threshold = 0.20;
minimumSize = 100;
maximumSize = 2000;
mode = 'sample';
source = 'Unspecified Source';
age = 'Unspecified Age';
debug = 0;

% Open the file:
fileID = fopen(filename);

textline = fgetl(fileID);
while ischar(textline)
	if length(textline) > 0			% If we're not a blank line...
		if textline(1) ~= '#'			%  .. and we're not a comment..
			% Then parse the entry:
			splitLine = strsplit(textline, '=');
			variable = strtrim(lower(splitLine(1)));
			options = strtrim(splitLine(2));

			% Since we seemingly can't do switch/case with variable-length strings, we'll do
			% a lot of if/else statements.  Ugly, but workable:

			if strcmp(variable, 'directory') == 1
				% If the option is a directory name, assign it
				directory = options{1};		

			elseif strcmp(variable, 'output') == 1
				% If the option is an output name, assing it
				output = options{1};				

			elseif strcmp(variable, 'tag') == 1
				% If the option is a tag name, assign it
				tag = options{1};					

			elseif strcmp(variable, 'threshold') == 1
				% Check how many arguments we're passing as options:
				options = strtrim(strsplit(options{:}));
				if length(options) == 5
					% We have a beginning, end, and step size:
					startvalue = options{1};
					endvalue = options{3};
					by = options{5};
					expression = sprintf('%s:%s:%s', startvalue, by, endvalue);
					threshold = eval(expression);
				elseif length(options) == 3
					% We have a beginning and end, use default step size of 0.01:
					startvalue = options{1};
					endvalue = options{3};
					by = '0.01';
					expression = sprintf('%s:%s:%s', startvalue, by, endvalue);
					threshold = eval(expression);
				elseif length(options) == 1
					% Convert to double and assign the value:
					threshold = str2double(options{1});
				else
					% We don't know what to do with this - flag an error and exit:
					fprintf('Not sure how to process the threshold values: %s\n', textline);
					exit(1);
				end

			elseif strcmp(variable, 'minimumsize') == 1
				% Convert to double and assign:
				minimumSize = str2double(options{1});

			elseif strcmp(variable, 'maximumsize') == 1
				% Convert to double and assign:
				maximumSize = str2double(options{1});

			elseif strcmp(variable, 'mode') == 1
				% Assingn to variable:
				mode = options{1};

			elseif strcmp(variable, 'source') == 1
				% Assingn to variable:
				source = options{1};

			elseif strcmp(variable, 'age') == 1
				% Assingn to variable:
				age = options{1};

			elseif strcmp(variable, 'debug') == 1
				% Assingn to variable:
				if strcmpi(options{1}, 'off') == 1
					debug = 0;
				elseif strcmpi(options{1}, 'low') == 1
					debug = 1;
				elseif strcmpi(options{1}, 'high') == 1
					debug = 2;
				else 
					debug = 0;
				end

			else
				fprintf('Unrecognized variable!\n');
			end
			%disp(textline);
		end
	end
	textline = fgetl(fileID);
end

fclose(fileID);

% Now assemble the settings array:

% First, check if the directory we've been given has TIFs or subdirectories:
%TIFFs = dir(fullfile(directory, '*.tif'));
%
%if size(TIFFs, 1) == 0
%	directories = dir(directory);
%	directories = directories(directories.isdir);
%files = {files.name};
%
%files = fullfile(directory, files);
%numFiles = length(files);


% Assume, for now, that only one directory will be used - directory, output and tag are all size 1.
% Similarly, assume for now that only threshold changes - min/max sizes do not.
numDirectories = length(directory);
numSettings = length(threshold);

% Set the time of this run:
currentTime = clock;
timestamp = sprintf('%04d-%02d-%02d at %02d:%02d:%02d', currentTime(1), currentTime(2), currentTime(3), currentTime(4), currentTime(5), int32(currentTime(6)));

settings = repmat(struct('directory', directory, 'output', output, 'tag', tag, 'threshold', [], 'minimumSize', minimumSize, 'maximumSize', maximumSize, ...
									       'age', age, 'source', source, 'mode', mode, 'debug', debug, 'timestamp', timestamp, 'micronsPerPixel', 0.0), 1, numSettings);

for n = 1:length(threshold)
	settings(n).threshold = threshold(n);
end



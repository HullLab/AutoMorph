function settings = parseSettings(filename)
% Modified from B. Dobbins' code
% Parses control file and pulls variable values for use in batch2dmorph.m

% Open the file:
fileID = fopen(filename);

textline = fgetl(fileID);
while ischar(textline)
	if ~isempty(textline)			% If we're not a blank line...
		if textline(1) ~= '#'			%  .. and we're not a comment..
			% Then parse the entry:
			splitLine = strsplit(textline, '=');
			variable = strtrim(lower(splitLine(1)));
            options = strtrim(splitLine(2:end));
			% Since we seemingly can't do switch/case with variable-length strings, we'll do
			% a lot of if/else statements.  Ugly, but workable:

			if strcmp(variable, 'directory') == 1
				% If the option is a directory name, assign it
                directory = strjoin(options,'=');

			elseif strcmp(variable, 'image_extension') == 1
				% If the option is an image extension, assign it
				image_extension = options{1};				

			elseif strcmp(variable, 'sampleid') == 1
				% If the option is a sampleID name, assign it
				sampleID = options{1};					
                
			elseif strcmp(variable, 'output_filename') == 1
                % If the option is the output filename, assign it
                if strcmp(options{1},'[]') == 1
                    output_filename = [];
                else
                    output_filename = options{1};
                end

			elseif strcmp(variable, 'microns_per_pixel_x') == 1
				% Convert to double and assign:
                if strcmp(options{1},'[]') == 1
                    microns_per_pixel_X = [];
                else
                    microns_per_pixel_X = str2double(options{1});
                end
                
            elseif strcmp(variable, 'microns_per_pixel_y') == 1
				% Convert to double and assign:
                if strcmp(options{1},'[]') == 1
                    microns_per_pixel_Y = [];
                else
                    microns_per_pixel_Y = str2double(options{1});
                end

			elseif strcmp(variable, 'get_coordinates') == 1
				% Convert to boolean and assign:
				if strcmp(options{1},'true') || strcmp(options{1},'[]')
                    get_coordinates = true;
                elseif strcmp(options{1},'false')
                    get_coordinates = false;
                end
                   
            elseif strcmp(variable, 'save_intermediates') == 1
				% Convert to boolean and assign:
				if strcmp(options{1},'true') == 1
                    save_intermediates = true;
                elseif strcmp(options{1},'false') == 1 || strcmp(options{1},'[]') == 1
                    save_intermediates = false;
                end
           
			elseif strcmp(variable, 'intensity_range_in') == 1
				if strcmp(options{1},'[]') == 1
                    intensity_range_in = [];
                else
                    splitHalf = strsplit(options{1},' ');
                    splitLeft = strsplit(splitHalf{1},'[');
                    splitRight = strsplit(splitHalf{2},']');
                    left = str2double(splitLeft{2});
                    right = str2double(splitRight{1});
                    intensity_range_in = [left right];
                end
                    
            elseif strcmp(variable, 'intensity_range_out') == 1
				if strcmp(options{1},'[]') == 1
                    intensity_range_out = [];
                else
                    splitHalf = strsplit(options{1},' ');
                    splitLeft = strsplit(splitHalf{1},'[');
                    splitRight = strsplit(splitHalf{2},']');
                    left = str2double(splitLeft{2});
                    right = str2double(splitRight{1});
                    intensity_range_out = [left right];
                end

            elseif strcmp(variable, 'gamma') == 1
				% Assign to variable:
                if strcmp(options{1},'[]') == 1
                    gamma = [];
                else
                    gamma = str2double(options{1});
                end

			elseif strcmp(variable, 'threshold_adjustment') == 1
				% Assign to variable:
				if strcmp(options{1},'[]') == 1
                    threshold_adjustment = [];
                else
                    threshold_adjustment = str2double(options{1});
                end
           
            elseif strcmp(variable,'smoothing_sigma') == 1
                if strcmp(options{1},'[]') == 1
                    smoothing_sigma = [];
                else
                    smoothing_sigma = str2double(options{1});
                end
                
            elseif strcmp(variable,'limit') == 1
                if strcmp(options{1},'[]') == 1
                    limit = [];
                else
                    limit = str2double(options{1});
                end
                
			elseif strcmp(variable, 'write_csv') == 1
				% Convert to boolean and assign:
				if strcmp(options{1},'true') == 1
                    write_csv = true;
                elseif strcmp(options{1},'false') == 1 || strcmp(options{1},'[]') == 1
                    write_csv = false;
                end
     
			elseif strcmp(variable, 'downsample') == 1
				% Convert to boolean and assign:
				if strcmp(options{1},'true') || strcmp(options{1},'[]')
                    downsample = true;
                elseif strcmp(options{1},'false')
                    downsample = false;
                end               
                    
            elseif strcmp(variable,'num_points') == 1
                if strcmp(options{1},'[]') == 1
                    num_points = [];
                else
                    num_points = str2double(options{1});
                end

			else
				fprintf('Unrecognized variable!\n');
            end
		end
	end
	textline = fgetl(fileID);
end

fclose(fileID);

% Set the time of this run:
currentTime = clock;
timestamp = sprintf('%04d-%02d-%02d at %02d:%02d:%02d', currentTime(1), currentTime(2), currentTime(3), currentTime(4), currentTime(5), int32(currentTime(6)));

% Now assemble the settings array:
settings = struct();
settings.directory = directory;
settings.image_extension = image_extension;
settings.sampleID = sampleID;
settings.output_filename = output_filename;
settings.microns_per_pixel_X = microns_per_pixel_X;
settings.microns_per_pixel_Y = microns_per_pixel_Y;
settings.get_coordinates = get_coordinates;
settings.save_intermediates = save_intermediates;
settings.intensity_range_in = intensity_range_in;
settings.intensity_range_out = intensity_range_out;
settings.gamma = gamma;
settings.threshold_adjustment = threshold_adjustment;
settings.smoothing_sigma = smoothing_sigma;
settings.limit = limit;
settings.write_csv = write_csv;
settings.downsample = downsample;
settings.num_points = num_points;

end

function batch2dmorph(directory,output_dir,image_extension,sampleID,microns_per_pixel_X,microns_per_pixel_Y,get_coordinates,save_intermediates,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,smoothing_sigma,noise_limit,downsample,num_points,draw_ar)
%Output:
%   Outputs a comma-delimited file named 'sampleID_morph2d_properties.csv'
%   (or 'output_filename_morph2d_properties.csv' if output_filename is specified)
%   containing morphological properties specified in measuremorph.m for all
%   objects in the folder.
%
%   Also outputs comma-delimited files named 'sampleID_coordinates_original.csv'
%   and 'sampleID_coordinates_smoothed.csv' (or 'output_filename_original_coordinates.csv'
%   if output_filename is specified, etc.) containing unsmoothed and smoothed
%   coordinates for all objects in the folder.
%
%   A text file containing all parameter settings named 'sampleID_parameters.csv'
%   is also outputted.
%
%   In addition, a file named 'sampleID_skipped.txt' is generated,
%   containing a list of all image files in the folder that are either
%   foram-less or require further manual manipulation to obtain a credible
%   outline.
%
%   If draw_AR == true, an image containing the smoothed outline of the
%   object, the minimum bounding box, and aspect ratio is outputted, along
%   with a text file named 'sampleID_aspectratios.csv'. Note that
%   if draw_AR == true, then get_coordinates must also be true.
%
%   Finally, a log file named 'sapmpleID_log.txt' is also outputted.
%
%Input Variables:
%   See the run2dmorph manual for explanations of all input variables.
%
%   NOTE: The function minBoundingBox.m by Julien Diener must be available
%   (https://tinyurl.com/m3md3l2).

version_number = '2016.09.26';

% Check number of arguments and set default values as necessary
narginchk(4,18);
if ~exist('output_dir','var') || isempty(output_dir), output_dir = fullfile(directory,'morph2d'); end
if ~exist('microns_per_pixel_X','var') || isempty(microns_per_pixel_X), microns_per_pixel_X = 1; end
if ~exist('microns_per_pixel_Y','var') || isempty(microns_per_pixel_Y), microns_per_pixel_Y = 1; end
if ~exist('get_coordinates','var') || isempty(get_coordinates), get_coordinates = true; end
if ~exist('save_intermediates','var') || isempty(save_intermediates), save_intermediates = false; end
if ~exist('intensity_range_in','var') || isempty(intensity_range_in), intensity_range_in = [0 0.2]; end
if ~exist('intensity_range_out','var') || isempty(intensity_range_out), intensity_range_out = [0 1]; end
if ~exist('gamma','var') || isempty(gamma), gamma = 2; end
if ~exist('threshold_adjustment','var') || isempty(threshold_adjustment), threshold_adjustment = 0; end
if ~exist('smoothing_sigma','var') || isempty(smoothing_sigma), smoothing_sigma = 7; end
if ~exist('noise_limit','var') || isempty(noise_limit), noise_limit = 0.05; end
if ~exist('downsample','var') || isempty(downsample), downsample = true; end
if ~exist('num_points','var') || isempty(num_points), num_points = 100; end
if ~exist('draw_ar','var') || isempty(draw_ar), draw_ar = true; end

% Change working directory to designed path
cd(directory);

% Make output directory if it doesn't exist
if ~exist('output_dir','dir'), mkdir(output_dir); end

% Start log file
diary(fullfile(output_dir,strcat(sampleID,'_log.txt')));
diary on

% Print version number
fprintf('Run2dmorph Version: %s\n\n',version_number);

% Print starting time and date
fprintf('Edge detection started: %s\n\n',datestr(now));

% Grab all files in folder with designated file extension
files = dir(strcat('*',image_extension));

% Initialize tables for storing morph properties and coordinates
final_table_morph = table();
final_table_coords_original = table();
final_table_coords_smoothed = table();

% Initialize data-storing arrays
skipped = [];
if draw_ar == true
    AR_table = table([],[],[],[],[],'VariableNames',{'sampleID','objectID','height','width','aspect_ratio'});
end

% Loop through all image files
for file = files'
    % Square image
    original_image = imread(file.name);
    size_original_image = size(original_image);
    new_height = ceil(size_original_image(1) * microns_per_pixel_Y);
    new_width = ceil(size_original_image(2) * microns_per_pixel_X);
    new_image = imresize(original_image,[new_height,new_width]);
    
    fprintf('Extracting outline: %s\n',file.name)
    % Force image to RGB mode with three layers
    rgb_image = new_image(:,:,1:3);
    % Extract 2D outline
    [obj_final,obj_edge,obj_smooth,sampleID,objectID] = extract2doutline(rgb_image,file.name,output_dir,sampleID,save_intermediates,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,smoothing_sigma,noise_limit); 
    % Determine if outline is discontinuous or non-existent (e.g., no foram
    % in source image), skip additional processing, and add it to list of
    % skipped images
    temp_perimeter_bumpy = regionprops(obj_edge,'Perimeter');
    temp_perimeter_smooth = regionprops(obj_smooth,'Perimeter');
    temp_area = regionprops(obj_final,'Area');
    if (length(temp_perimeter_bumpy) == 1) && (length(temp_perimeter_smooth) == 1) && (length(temp_area) == 1) && ~(max(obj_edge(:)) == 0)
        % Obtain morphological measurements
        temp_table = struct2table(measuremorph(output_dir,obj_final,obj_edge,obj_smooth,sampleID,objectID));
        % Append morphological measurements for current object to final table
        % of measurements
        final_table_morph = vertcat(final_table_morph,temp_table);
    	% Obtain coordinates if necessary
        if get_coordinates == true
            [final_table_original,final_table_smoothed] = extractcoordinates(output_dir,obj_edge,obj_smooth,sampleID,objectID,downsample,num_points);
            % If draw_AR == true, output sampleID_objectID_aspectratios.csv' and
            % corresponding images.
            if draw_ar == true
                [H,W,aspect_ratio] = aspectRatio(output_dir,sampleID,objectID,final_table_smoothed);
                AR_struct = struct('sampleID',char(sampleID),'objectID',char(objectID),'height',H,'width',W,'aspect_ratio',aspect_ratio);
                temp_table = struct2table(AR_struct);
                AR_table = [AR_table;temp_table];
            end
            final_table_coords_original = vertcat(final_table_coords_original,final_table_original);
            final_table_coords_smoothed = vertcat(final_table_coords_smoothed,final_table_smoothed);
        end 
    else    
        skipped = [skipped file.name];
        fprintf('Skipped: %s\n',file.name)
        continue
    end
end

% Write final output files
    % Write final tables
    writetable(final_table_morph,fullfile(output_dir,strcat(sampleID,'_morph2d_properties.csv')));
    if get_coordinates == true
        writetable(final_table_coords_original,fullfile(output_dir,strcat(sampleID,'_coordinates_original.csv')));
        writetable(final_table_coords_smoothed,fullfile(output_dir,strcat(sampleID,'_coordinates_smoothed.csv')));
    end
    % Write aspect ratio table if draw_AR == true
    if draw_ar == true
        writetable(AR_table,fullfile(output_dir,strcat(sampleID,'_aspectratio.csv')));
    end
    % Save parameter values
    parameters = {};
    parameters.version_number = version_number;
    parameters.intensity_range_in_low = intensity_range_in(1);
    parameters.intensity_range_in_high = intensity_range_in(2);
    parameters.intensity_range_out_low = intensity_range_out(1);
    parameters.intensity_range_out_high = intensity_range_out(2);
    parameters.gamma = gamma;
    parameters.threshold_adjustment = threshold_adjustment;
    parameters.smoothing_sigma = smoothing_sigma;
    parameters.noise_limit = noise_limit;
    parameters.microns_per_pixel_X = microns_per_pixel_X;
    parameters.microns_per_pixel_Y = microns_per_pixel_Y;
    if downsample == true, parameters.downsample = 'true'; else parameters.downsample = 'false'; end
    parameters.num_points = num_points;
    % Write parameter values to file
    writetable(struct2table(parameters),fullfile(output_dir,strcat(sampleID,'_parameters.csv')));
    % Write file containing names of skipped images if they exist, and copy images to
    % 'no_outline_extracted' folder
    if ~isempty(skipped)
        % Make 'no_outline_extracted' folder if it doesn't exist
        if ~exist(fullfile(output_dir,'no_outline_extracted'),'dir'), mkdir(fullfile(output_dir,'no_outline_extracted')); end
        % Prepare file names
        split = strsplit(skipped,image_extension);
        % Open file to which names of skipped images will be written
        skipped_file = fopen(fullfile(output_dir,strcat(sampleID,'_skipped.txt')),'w');
        % Loop through skipped files and 1) write names to file; and 2)
        % copy original image file to 'no_outline_extracted' folder
        for object = split(1:end-1)
            fprintf(skipped_file,'%s\n',object{1});
            copyfile(strcat(object{1},image_extension),fullfile(output_dir,'no_outline_extracted',strcat(object{1},image_extension)));
        end
        fclose(skipped_file);
    end
    
% End logging
fprintf('\nEdge detection complete: %s\n',datestr(now));
diary off
end
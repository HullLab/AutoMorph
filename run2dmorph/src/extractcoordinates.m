function [final_table_original,final_table_smoothed] = extractcoordinates(output_dir,obj_edge,obj_smooth,sampleID,objectID,downsample_bool,num_points)
%Output:
%
%   FILES:
%   If write_csv == true, this function outputs two comma-delimited files,
%   one containing the x,y-coordinates of the unsmoothed object outline,
%   the other containing the x,y-coordinates of the smoothed object
%   outline. These files are named
%   'sampleID_objectID_coordinates_original.csv' (unsmoothed) and
%   'sampleID_objectID_coordinates_smoothed.csv' (smoothed).
%
%   All output files are saved to a directory named 'morph2d' nested in the
%   folder containing the image file(s).
%   
%Output Variables:
%   final_table_original: a table containing the x,y-coordinates of the
%   unsmoothed object outline
%
%   final_table_smoothed: a table containing the x,y-coordintaes of the
%   smoothed object outline
%
%Input Variables:
%
%   obj_edge: a logical matrix specifying the edge of the foram in the
%   input image (output from the extract2doutline function). (REQUIRED)
%
%   obj_smooth: a logical matrix specifying the smoothed edge of the foram
%   in the input image (output from extract2doutline function).
%   (REQUIRED)
%
%   sampleID: a string identifying the sample number of the object in
%   question (output from extract2doutline function). (REQUIRED)
%
%   objectID: a string identifying the object whose morphological
%   properties are being measured (output from extract2doutline function).
%   (REQUIRED)
%
%   downsample_bool: a boolean specifying if coordinates should be downsampled.
%   (Default: true)
%
%   num_points: an integer specifying the number of points desired in the
%   output coordinates (only necessary if downsample == true). (Default: 100)
%
%   write_csv: a boolean specifying whether a csv file should be written.
%   (Default value: false)

% Check number of input arguments and set up default values as necessary.
narginchk(4,7);
if ~exist('downsample_bool','var') || isempty(downsample_bool), downsample_bool = true; end
if ~exist('min_points','var') || isempty(num_points), num_points = 100; end

% Blur original images to allow for resampling with higher fidelity
    % Convert edges to doubles
    original_double = double(obj_edge);
    smooth_double = double(obj_smooth);
    % Blur using gaussian blur
    gfilter = fspecial('gaussian');
    original_blurred = imfilter(obj_edge,gfilter);
    smooth_blurred = imfilter(obj_smooth,gfilter);

% Obtain xy-coordinates
boundary_original = bwboundaries(original_blurred);
boundary_smooth = bwboundaries(smooth_blurred);
xy_original = boundary_original{1};
xy_smooth = boundary_smooth{1};
x_original = xy_original(:,2);
x_smooth = xy_smooth(:,2);
y_original = -xy_original(:,1);
y_smooth = -xy_smooth(:,1);

% Downsample if necessary
if downsample_bool == true    
	% Determine final number of points
    downsampling_factor_original = 2;
    downsampling_factor_smooth = 2;
    while (length(x_original) / downsampling_factor_original > num_points), downsampling_factor_original = downsampling_factor_original + 1; end
    while (length(x_smooth) / downsampling_factor_smooth > num_points), downsampling_factor_smooth = downsampling_factor_smooth + 1; end
    % Downsample points
    x_original_downsample = downsample(x_original,downsampling_factor_original - 1);
    y_original_downsample = downsample(y_original,downsampling_factor_original - 1);
    x_smooth_downsample = downsample(x_smooth,downsampling_factor_smooth - 1);
    y_smooth_downsample = downsample(y_smooth,downsampling_factor_smooth - 1);
    % Resample to get exact number of points
    x_original_coords = resample(x_original_downsample,num_points,length(x_original_downsample));
    y_original_coords = resample(y_original_downsample,num_points,length(y_original_downsample));
    x_smooth_coords = resample(x_smooth_downsample,num_points,length(x_smooth_downsample));
    y_smooth_coords = resample(y_smooth_downsample,num_points,length(y_smooth_downsample));
end

% Generate final tables 
	% Generate sampleID and objectID arrays
    sampleID_rep_original = repmat(sampleID,length(x_original_coords),1);
    objectID_rep_original = repmat(objectID,length(x_original_coords),1);
    sampleID_rep_smoothed = repmat(sampleID,length(x_smooth_coords),1);
    objectID_rep_smoothed = repmat(objectID,length(x_smooth_coords),1);
    % Generate sampleID and objectID tables
    sampleID_table_original = table(sampleID_rep_original,'VariableNames',{'SampleID'});
    objectID_table_original = table(objectID_rep_original,'VariableNames',{'ObjectID'});
    sampleID_table_smoothed = table(sampleID_rep_smoothed,'VariableNames',{'SampleID'});
    objectID_table_smoothed = table(objectID_rep_smoothed,'VariableNames',{'ObjectID'});
    % Convert coordinate data to tables
    original_coords_table = array2table([x_original_coords,y_original_coords],'VariableNames',{'x','y'});
    smoothed_coords_table = array2table([x_smooth_coords,y_smooth_coords],'VariableNames',{'x_smoothed','y_smoothed'});
    % Concatenate into final tables
    final_table_original = horzcat(sampleID_table_original,objectID_table_original,original_coords_table);
    final_table_smoothed = horzcat(sampleID_table_smoothed,objectID_table_smoothed,smoothed_coords_table);
end
function morphproptable = measuremorph(obj_final,obj_edge,obj_smooth,sampleID,objectID,microns_per_pixel,write_csv)
%Output:
%
%   FILES:
%   If write_csv == true, this function outputs a comma-delimited file named
%   'sampleID_objectID_morph2d_properties' into a folder named 'morph2d'.
%
%   VARIABLES:
%   morphproptable: a table containing the following morphometric properties:
%   Area, Eccentricity, Perimeter, MinorAxisLength, MajorAxisLength,
%   Rugosity
%   See:
%       http://www.mathworks.com/help/images/ref/regionprops.html
%
%Input Variables:
%
%   obj_final: a logical matrix specifying the black and white isolated
%   image of the foram in the input image (output from the extract2doutline
%   function). (REQUIRED)
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
%   microns_per_pixel: a number specifying the numbers of microns per
%   pixel. If specified, measurements will be divided by this value and
%   reported in microns. Otherwise, measurements will be in units of
%   pixels. (Default value: 1)
%
%   write_csv: a boolean specifying whether a csv file should be written.
%   (Default value: false)

% Check number of input arguments and set up default values as necessary.
narginchk(5,7);
if ~exist('microns_per_pixel','var') || isempty(microns_per_pixel), microns_per_pixel = 1; end
if ~exist('write_csv','var') || isempty(write_csv), write_csv = false; end

% Calculate area, eccentricity, minor and major axis length 
props = regionprops(obj_final,'Area','Eccentricity','MinorAxisLength','MajorAxisLength');

% Calculate perimeter and rugosity
bumpy_perim = regionprops(obj_edge,'Perimeter');
smooth_perim = regionprops(obj_smooth,'Perimeter');
props.Perimeter = bumpy_perim.Perimeter;
props.Rugosity = bumpy_perim.Perimeter / smooth_perim.Perimeter;

% Apply micron/pixel conversion if necessary
if microns_per_pixel ~= 1
    props.Area = props.Area / microns_per_pixel;
    props.Perimeter = props.Perimeter / microns_per_pixel;
    props.MinorAxisLength = props.MinorAxisLength / microns_per_pixel;
    props.MajorAxisLength = props.MajorAxisLength / microns_per_pixel;
end

% Add sample and object name and generate final data table
props.SampleID = char(sampleID);
props.ObjectID = char(objectID);
morphproptable = props;

% Write csv file
if write_csv == true
    % Make output directory if it doesn't exist
    if ~exist('morph2d','dir'), mkdir('morph2d'); end
    % Check current architecture and assign appropriate path
    % dividor (solidus or reverse solidus)
    architecture = computer;
    if strcmp(computer,'MACI64') == 1 || strcmp(computer,'GLNXA64') == 1, path_divider = '/'; else path_divider = '\'; end
    % Write final table
    final_table = struct2table(morphproptable);
    writetable(final_table,strcat('morph2d',path_divider,sampleID,'_',objectID,'_morph2d_properties.csv'));
end
end

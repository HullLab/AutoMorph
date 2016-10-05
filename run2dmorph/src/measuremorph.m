function morphproptable = measuremorph(output_dir,obj_final,obj_edge,obj_smooth,sampleID,objectID)
%Output:
%
%   FILES:
%   If write_csv == true, this function outputs a comma-delimited file named
%   'sampleID_objectID_morph2d_properties' into a folder named 'morph2d'.
%
%Output Variables:
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
%   write_csv: a boolean specifying whether a csv file should be written.
%   (Default value: false)
%
%   draw_AR: a boolean specifying whether an image of the smoothed object,
%   minimum bounding box, and aspect ratio of the object should be written.
%   (Default value: false)

% Check number of input arguments and set up default values as necessary.
narginchk(6,6);

% Calculate area, eccentricity, minor and major axis length 
props = regionprops(obj_final,'Area','Eccentricity','MinorAxisLength','MajorAxisLength');

% Calculate perimeter and rugosity
bumpy_perim = regionprops(obj_edge,'Perimeter');
smooth_perim = regionprops(obj_smooth,'Perimeter');
props.Perimeter = bumpy_perim.Perimeter;
props.Rugosity = bumpy_perim.Perimeter / smooth_perim.Perimeter;

% Add sample and object name and generate final data table
props.SampleID = char(sampleID);
props.ObjectID = char(objectID);
morphproptable = props;

end

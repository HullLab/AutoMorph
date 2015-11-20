function getVolumes(morph3d_path,image_name,mbb_path,xy_points,z_values,coordinates,downsample_grid_size)
% Calculates total volume of object assuming 1) dome base; 2) pyramid base;
% and 3) cube base. Outputs a .csv file with all three measures. Also outputs total surface
% area estimates for each type of base.
%
% Dependency:
%       minBoundingBox.m (c) 2011, Julien Diener
%           https://www.mathworks.com/matlabcentral/fileexchange/31126-2d-minimal-bounding-box/content/minBoundingBox.m

% Add location of minBoundingBox.m to the path
addpath(mbb_path);

% Find minimum bounding box
bb = minBoundingBox(xy_points');
x = bb(1,:);
y = bb(2,:);

% Get width and height of minimum bounding box
distances = pdist(bb','euclidean');
W = min(distances);
H = median(distances);

% Get (x,y) coordinates of four corners of minimum bounding box
point1_x = x(2);
point1_y = y(2);
point2_x = (abs(x(1)) + abs(x(2))) / 2;
point2_y = (abs(y(1)) + abs(y(2))) / 2;
point3_x = (abs(x(2)) + abs(x(3))) / 2;
point3_y = (abs(y(2)) + abs(y(3))) / 2;
point4_x = -point1_x + point2_x + point3_x;
point4_y = -point1_y + point2_y + point3_y;

% Calculate volume of top half of object
top_volume = sum(coordinates(:) - min(z_values(:)));

% Calculate volume of bottom half (dome)
ellipsoid_semi_x = H/2;
ellipsoid_semi_y = W/2;
ellipsoid_semi_z = z_values(1);
bottom_volume_dome = 0.5 * (4/3) * pi * ellipsoid_semi_x * ellipsoid_semi_y * ellipsoid_semi_z;

% Calculate volume of bottom half (cube)
bottom_volume_cube = W * H * z_values(1);

% Calculate volume of bottom half (pyramid)
bottom_volume_pyramid = bottom_volume_cube / 3;

% Get total volumes
total_volume_dome = top_volume + bottom_volume_dome;
total_volume_cube = top_volume + bottom_volume_cube;
total_volume_pyramid = top_volume + bottom_volume_pyramid;

% Build output file name and path
output_filename = strcat(image_name,'_volumes.csv');
output_path = fullfile(morph3d_path,'stackfocused',image_name,output_filename);

% Write volumes to file
volume_file = fopen(output_path,'w');
if isempty(downsample_grid_size), downsample_grid_size = 10; end
fprintf(volume_file,'object,volume_dome,volume_cube,volume_pyramid,grid_size,height,width\r%s,%.4f,%.4f,%.4f,%d,%.2f,%.2f',image_name,total_volume_dome,total_volume_cube,total_volume_pyramid,downsample_grid_size,H,W);
fclose(volume_file);

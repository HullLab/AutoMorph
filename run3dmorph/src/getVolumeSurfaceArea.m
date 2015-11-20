function getVolumes(morph3d_path,image_name,mbb_path,xy_points,z_values,coordinates,top_surface_area,downsample_grid_size)
% Calculates total volume of object assuming 1) ellipsoid base; 2) pyramid base;
% and 3) cuboid base. Outputs a .csv file with all three measures. Also outputs total surface
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
L = median(distances);
H = z_values(1);
height = z_values(end);

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
z_coords = coordinates(:,3);
top_volume = sum(z_coords(:) - min(z_values(:)));

% Calculate volume and surface area of of bottom half (ellipsoid)
ellipsoid_semi_x = L/2;
ellipsoid_semi_y = W/2;
ellipsoid_semi_z = H;
bottom_volume_ellipsoid = 0.5 * (4/3) * pi * ellipsoid_semi_x * ellipsoid_semi_y * ellipsoid_semi_z;
p = 1.6075;
surface_area_ellipsoid = (4 * pi * ((ellipsoid_semi_z^p * ellipsoid_semi_x^p + ellipsoid_semi_z^p * ellipsoid_semi_y^p + ellipsoid_semi_x^p * ellipsoid_semi_y^p) / 3)^(1/p)) / 2;

% Calculate volume and surface area of bottom half (cuboid)
bottom_volume_cuboid = W * L * z_values(1);
surface_area_cuboid = (2 * (L * W + W * H + H * L)) - (L * W);

% Calculate volume and surface area of bottom half (pyramid)
bottom_volume_pyramid = bottom_volume_cuboid / 3;
surface_area_pyramid = L * sqrt((W / 2)^2 + H^2) + W * sqrt((L / 2)^2 + H^2);

% Get total surface areas
total_surface_area_ellipsoid = top_surface_area + surface_area_ellipsoid;
total_surface_area_cuboid = top_surface_area + surface_area_cuboid;
total_surface_area_pyramid = top_surface_area + surface_area_pyramid;

% Get total volumes
total_volume_ellipsoid = top_volume + bottom_volume_ellipsoid;
total_volume_cuboid = top_volume + bottom_volume_cuboid;
total_volume_pyramid = top_volume + bottom_volume_pyramid;

% Build output file name and path
output_filename = strcat(image_name,'_volumes.csv');
output_path = fullfile(morph3d_path,'stackfocused',image_name,output_filename);

% Write volumes to file
volume_file = fopen(output_path,'w');
if isempty(downsample_grid_size), downsample_grid_size = 10; end
fprintf(volume_file,'object,volume_ellipsoid,volume_cuboid,volume_pyramid,surface_area_ellipsoid,surface_area_cuboid,surface_area_pyramid,grid_size,height,width,length\r%s,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%d,%.2f,%.2f,%.2f',image_name,total_volume_ellipsoid,total_volume_cuboid,total_volume_pyramid,total_surface_area_ellipsoid,total_surface_area_cuboid,total_surface_area_pyramid,downsample_grid_size,height,W,L);
fclose(volume_file);
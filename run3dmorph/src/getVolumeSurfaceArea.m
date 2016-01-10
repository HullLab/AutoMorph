function getVolumeSurfaceArea(mbb_path,morph3d_path,image_name,z_values,xy_points,top_volume,top_surface_area,downsample_grid_size,area_2D,perimeter_2D,centroid_2D,final_table_original)
% Calculates total volume of object assuming 1) a conic base;
% 2) a cylindrical base; and 3) a dome base. Outputs a .csv file with both measures.
% Also outputs total surface area estimates for each type of base.

% Add location of minBoundingBox.m to the path
addpath(mbb_path);

% Find minimum bounding box and get its width and height
bb = minBoundingBox(xy_points');
distances = pdist(bb','euclidean');
W = min(distances);
L = median(distances);

% H = height from background to bottom of half-mesh; height = total height
% of object
H = z_values(1);
height = z_values(end);

% Calculate volume and surface area of of bottom half (dome)
ellipsoid_semi_x = L/2;
ellipsoid_semi_y = W/2;
ellipsoid_semi_z = H;
bottom_volume_dome = 0.5 * (4/3) * pi * ellipsoid_semi_x * ellipsoid_semi_y * ellipsoid_semi_z;
p = 1.6075;
surface_area_dome = (4 * pi * ((ellipsoid_semi_z^p * ellipsoid_semi_x^p + ellipsoid_semi_z^p * ellipsoid_semi_y^p + ellipsoid_semi_x^p * ellipsoid_semi_y^p) / 3)^(1/p)) / 2;

% Calculate volume and surface area of bottom half (cylinder)
bottom_volume_cylinder = area_2D * H;
surface_area_cylinder = (perimeter_2D * H) + area_2D;

% Calculate volume and surface area of bottom half (cone)
bottom_volume_cone = bottom_volume_cylinder / 3;
surface_area_cone = genConeSurfaceArea(centroid_2D,H,final_table_original);

% Get total surface areas
total_surface_area_dome = top_surface_area + surface_area_dome;
total_surface_area_cylinder = top_surface_area + surface_area_cylinder;
total_surface_area_cone = top_surface_area + surface_area_cone;

% Get total volumes
total_volume_dome = top_volume + bottom_volume_dome;
total_volume_cylinder = top_volume + bottom_volume_cylinder;
total_volume_cone = top_volume + bottom_volume_cone;

% Build output file name and path
output_filename = strcat(image_name,'_volume_surface_area.csv');
output_path = fullfile(morph3d_path,'stackfocused',image_name,output_filename);

% Write volumes to file
volume_file = fopen(output_path,'w');
if isempty(downsample_grid_size), downsample_grid_size = 10; end
fprintf(volume_file,'object,volume_dome,volume_cylinder,volume_cone,volume_top,surface_area_dome,surface_area_cylinder,surface_area_cone,surface_area_top,grid_size,height,width,length\r%s,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%d,%.2f,%.2f,%.2f',image_name,total_volume_dome,total_volume_cylinder,total_volume_cone,top_volume,total_surface_area_dome,total_surface_area_cylinder,total_surface_area_cone,top_surface_area,downsample_grid_size,height,W,L);
fclose(volume_file);
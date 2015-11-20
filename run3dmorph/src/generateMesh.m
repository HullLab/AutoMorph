function [skipped,coordinates,top_surface_area,xy_points,z_values,X,Y,Z] = generateMesh(focused_image_rgb,height_map,image_name,sampleID,calibration,num_slices,zstep,kernel_size_OF,downsample_grid_size)
% Takes heightmap, grayscale focused image, and RGB focused image and
% generates a 3D mesh.

% Check variables and set defaults as necessary
narginchk(8,10);
if ~exist('kernel_size_OF','var') || isempty(kernel_size_OF), kernel_size_OF = 19; end
if ~exist('downsample_grid_size','var') || isempty(downsample_grid_size), downsample_grid_size = 10; end

% Read in input files
heightmap = imread(height_map);
focused_rgb = imread(focused_image_rgb);

% Resize images using pixel-to-micron calibration factor
resized_hm = resizePixelToMicron(heightmap,calibration);
resized_rgb = resizePixelToMicron(focused_rgb,calibration);

% Run 2D outline extraction for outline deletion
% ADD ABILITY HERE TO READ IN PERIMETER VALUES IF RUN2DMORPH HAS ALREADY
% BEEN RUN ON THE SAMPLES
[obj_final,~,~,~,~] = extract2doutline(resized_rgb,image_name,sampleID);
[obj_final_holes,~,~,~,~] = extract2doutline_nofill(resized_rgb,image_name,sampleID);

% Convert image formats
uint8_obj_final = uint8(obj_final);
heightmap_nobg = uint8_obj_final .* resized_hm;

% Scale heightmap according to number of slices and z-step size
scale = idivide(uint8(255),num_slices);
descaled_hm = (heightmap_nobg ./ scale);
zstep_scaled_hm = (double(descaled_hm) .* zstep);

% Run neighborhood filter to remove outliers
filtered = nlfilter(zstep_scaled_hm,[kernel_size_OF kernel_size_OF],@(matrix) outlierFilter(matrix));

% Get coordinates of non-zero pixels of z-step scaled heightmap (format:
% [index_x,index_y,grayscale_value])
[row_hm,column_hm,value_hm] = find(filtered);
coordinates_hm = horzcat(row_hm,column_hm,value_hm);

% Get number of points on each z level
z_hm = double(value_hm);
count_values = histc(z_hm,unique(z_hm));
count_matrix = [unique(z_hm) count_values];

% Get perimeter of 2D outline to determine which points lie below the rim
% of the object (noise to be deleted) - objects whose perimeter cannot be
% robustly calculated will be skipped
perim = regionprops(obj_final,'Perimeter');
if length(perim) ~= 1
    skipped = true;
    fprintf('Skipped: %s\n',image_name)
    return
else
    skipped = false;
end

% Determine outliers (< 1% number of points compared to total)
sum_values = sum(count_values);
included_heights = [];
for i = 1:numel(count_values)
    if ((count_values(i) / sum_values) > 0.01)
        included_heights = [included_heights i];
    end
end

if min(included_heights) ~= 1
	cutoff_height_lower = min(included_heights)-1;
else
	cutoff_height_lower = min(included_heights);
end
cutoff_height_upper = max(included_heights);

% Remove 'infinite black hole' artifacts if they exist
if ~isequal(obj_final,obj_final_holes)
	unique_z_values = unique(z_hm);
	if exist('cutoff_height_lower','var'),
		lowest_value = unique_z_values(cutoff_height_lower + 1);
	else
		lowest_value = unique_z_values(1);
	end
	holes = obj_final + -obj_final_holes;
	filtered_with_holes = filtered .* double(obj_final_holes);
	hole_values = holes .* lowest_value;
	adjusted = filtered_with_holes + hole_values;
	[row_hm,column_hm,value_hm] = find(adjusted);
	coordinates_hm = horzcat(row_hm,column_hm,value_hm);
	x_hm = double(row_hm);
	y_hm = double(column_hm);
	z_hm = double(value_hm);
	count_values = histc(z_hm,unique(z_hm));
	count_matrix = [unique(z_hm) count_values];
end

% Delete points above high cutoff level and below low cutoff level
if exist('cutoff_height_lower','var')
	low_cutoff = coordinates_hm(coordinates_hm(:,3) >= count_matrix(cutoff_height_lower,1),:);
	if exist('cutoff_height_upper','var')
    	high_low_cutoff = low_cutoff(low_cutoff(:,3) <= count_matrix(cutoff_height_upper,1),:);
    	z_values = unique(high_low_cutoff(:,3));
    	xy_points = [high_low_cutoff(:,1) high_low_cutoff(:,2)];
	else
    	z_values = unique(low_cutoff(:,3));
    	xy_points = [low_cutoff(:,1) low_cutoff(:,2)];
	end
else
	z_values = unique(coordinates_hm(:,3));
	xy_points = [coordinates_hm(:,1) coordinates_hm(:,2)];
end

% Convert coordinates to double format
if exist('high_low_cutoff','var')
    x = double(high_low_cutoff(:,1));
    y = double(high_low_cutoff(:,2));
    z = double(high_low_cutoff(:,3));
elseif exist('low_cutoff','var')
    x = double(low_cutoff(:,1));
    y = double(low_cutoff(:,2));
    z = double(low_cutoff(:,3));
else
	x = double(coordinates_hm(:,1));
	y = double(coordinates_hm(:,2));
	z = double(coordinates_hm(:,3));
end

% Calculate top surface area
top_surface_area = length(coordinates_hm);

% Downsample coordinates of 3D mesh
dxy_ds = downsample_grid_size;
x_edge = min(x):dxy_ds:max(x);
y_edge = min(y):dxy_ds:max(y);
[X,Y] = meshgrid(x_edge,y_edge);
Z = griddata(x,y,z,X,Y);
% Reshape grid data to single columns
x_ds_1col = reshape(X,[numel(X),1]);
y_ds_1col = reshape(Y,[numel(Y),1]);
z_ds_1col = reshape(Z,[numel(Z),1]);
% Remove NaNs
coords_tophalf_NaNs = [x_ds_1col y_ds_1col z_ds_1col];
coords_tophalf = coords_tophalf_NaNs(isnan(coords_tophalf_NaNs(:,3)) == 0,:);
coordinates = coords_tophalf;
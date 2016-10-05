function morph3dwrapper(run3dmorph_path,morph3d_path,focused_image_rgb,height_map,image_name,sampleID,macro_mode,unit,calibration,num_slices,zstep,kernel_size_OF,downsample_grid_size,savePDF,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,noise_limit)
% Runs suite of morph3D functions to:
%   1) Extract 3D Mesh from heightmap generated using StackFocuser
%   2) Generate 3D PDF (if generate_pdf == True)
%   3) Output OBJ file for downstream morphometrics processing

% Set necessary paths
mbb_path = run3dmorph_path;
geom3d_path = fullfile(run3dmorph_path,'geom3d-2014.10.13','geom3d','meshes3d');
mesh2pdf_path = fullfile(run3dmorph_path,'mesh2pdf');

% Generate mesh
time_start = datestr(now);
disp(strcat('Start: ',time_start))

try
	[skipped,coordinates,top_surface_area,z_values,xy_points,X,Y,Z,area_2D,perimeter_2D,centroid_2D,top_volume,final_table_original] = generateMesh(morph3d_path,focused_image_rgb,height_map,image_name,sampleID,macro_mode,calibration,num_slices,zstep,kernel_size_OF,downsample_grid_size,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,noise_limit);
catch
	warning('Cannot generate mesh!')
	exit()
end

if skipped == true
    % Isolate skipped object folder as necessary
    moveSkipped(morph3d_path,skipped,image_name);
    disp('Object %s skipped',image_name);    
else
    % Write coordinates file
    writeCoordinates(morph3d_path,image_name,coordinates);

    % Calculate (and write to .csv file) volumes assuming 1) dome base; 2) pyramid base; 3) cube base
    getVolumeSurfaceArea(mbb_path,morph3d_path,image_name,z_values,xy_points,top_volume,top_surface_area,downsample_grid_size,area_2D,perimeter_2D,centroid_2D,final_table_original,unit);
    
    % Write OBJ and OFF s
    writeOBJOFF(morph3d_path,image_name,geom3d_path,coordinates);
    
    % 3D PDF preprocessing (if specified)
    if isequal(savePDF,true) || isempty(savePDF)
    	pdfPreprocess(morph3d_path,mesh2pdf_path,image_name,X,Y,Z);
    end
time_end = datestr(now);
disp(strcat('End: ',time_end))
end



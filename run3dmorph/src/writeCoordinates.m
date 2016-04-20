function writeCoordinates(morph3d_path,image_name,coordinates)
% Writes comma-separated (.csv) file containing x-, y-, and z-coordinates
% of the object being processed.

output_file_name = strcat(image_name,'_coordinates.csv');
output_path = fullfile(morph3d_path,'stackfocused',image_name,output_file_name);
coords_table = table(coordinates(:,1),coordinates(:,2),coordinates(:,3),'VariableNames',{'x','y','z'});
writetable(coords_table,output_path);
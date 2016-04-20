function writeOBJOFF(morph3d_path,image_name,geom3d_path,coordinates)
% Generates faces and vertices for 3D mesh and writes them to an
% OBJ-formatted file.
% Dependencies:
%       pointCloud2mesh.m (geom3d package) (c) 2009, Brett Shoelson, (c)
%       2014, INRA
%           https://www.mathworks.com/matlabcentral/fileexchange/24484-geom3d

addpath(geom3d_path);
mesh = pointCloud2mesh(coordinates,[0 0 1],20);
vertices = mesh.vertices;
faces = mesh.triangles;

% Initialize output path/file name and make output directory
% OBJ
output_file_name_obj = strcat(image_name,'.obj');
output_path_obj = fullfile(morph3d_path,'obj_files');
if ~exist(output_path_obj,'dir'), mkdir(output_path_obj); end
% OFF
output_file_name_off = strcat(image_name,'.off');
output_path_off = fullfile(morph3d_path,'off_files');
if ~exist(output_path_off,'dir'),mkdir(output_path_off); end

% Get number of vertices and faces
num_rows_vertices = size(vertices,1);
num_rows_faces = size(faces,1);

% Initialize OBJ and OFF files and print header information
obj_file = fopen(fullfile(output_path_obj,output_file_name_obj),'w');
off_file = fopen(fullfile(output_path_off,output_file_name_off),'w');
header_obj = ['# ',image_name,'.obj\r\rg ',image_name,'\r\r'];
fprintf(off_file,'OFF\r%d %d 0\r',num_rows_vertices,num_rows_faces);
fprintf(obj_file,header_obj);

% Print vertices
for row = 1:num_rows_vertices
    current_row = vertices(row,:);
    fprintf(obj_file,'v %.2f %.2f %.2f\r',current_row(1),current_row(2),current_row(3));
    fprintf(off_file,'%.2f %.2f %.2f\r',current_row(1),current_row(2),current_row(3));
end
fprintf(obj_file,'\r\r');

% Print faces
for row = 1:num_rows_faces
    current_row = faces(row,:);
    fprintf(obj_file,'f %d %d %d\r',current_row(1),current_row(2),current_row(3));
    fprintf(off_file,'3 %d %d %d\r',current_row(1),current_row(2),current_row(3));
end

fclose(obj_file);
fclose(off_file);

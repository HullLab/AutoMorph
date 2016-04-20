function pdfPreprocess(morph3d_path,mesh2pdf_path,image_name,X,Y,Z)
% Builds necessary preproccessing files for generating 3D PDF of object
% being processed.
%
% Dependencies:
%       u3d_pre (c) 2010, Sven Koerner
%           staffhome.ecm.uwa.edu.au/~00053650/code/pointCloud2mesh.m
%       save_idtf.m (mesh2pdf package) (c) 2009, Douglas M. Schwarz, (c) 2010 Alexandre Gramfort
%           https://www.mathworks.com/matlabcentral/fileexchange/25383-matlab-mesh-to-pdf-with-3d-interactive-object
% 
% ____________
% Mesh -> IDTF -> U3D -> LaTeX -> 3D PDF

% Build and add necessary paths
addpath(mesh2pdf_path);
pdf3d_path = fullfile(morph3d_path,'pdf_3d');
idtf_path = fullfile(pdf3d_path,'idtf_files');
u3d_path = fullfile(pdf3d_path,'u3d_files');

% Create 'pdf_3d' and 'idtf_files' folders
if ~exist(pdf3d_path,'dir'), mkdir(pdf3d_path); end
if ~exist(idtf_path,'dir'), mkdir(idtf_path); end

% Generate surface object to construct mesh
set(0,'DefaultFigureVisible','off');
surf(X/100,Y/100,Z/100);
axis equal;
colormap(gca,parula)
fvc = u3d_pre;
[nx,ny,nz] = surfnorm(X/100,Y/100,Z/100);
numels = size(nx);
normals = reshape([nx ny nz],numels(1)*numels(2),3);

% Write IDTF file for 3D PDF generation (remove '.' from file name if necessary)
if ~isempty(strfind(image_name,'.'))
	split_name = strsplit(image_name,'.');
	image_name = strjoin(split_name,'');
end
idtf_filename = strcat(image_name,'.idtf');
idtf_file_path = fullfile(idtf_path,idtf_filename);
save_idtf(idtf_file_path,fvc.vertices,uint32(fvc.faces),fvc.facevertexcdata,normals);
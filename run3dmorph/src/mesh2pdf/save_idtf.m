function [] = save_idtf(filename,points,faces,face_vertex_data,normals)
%   SAVE_IDTF   Save mesh in basic IDTF format
%       [] = SAVE_IDTF(FILENAME,POINTS,FACES,FACE_VERTEX_DATA)
%
%   Created by Alexandre Gramfort on 2009-04-21.
%   Copyright (c)  Alexandre Gramfort. All rights reserved.

% $Id: save_idtf.m 2 2009-08-26 15:05:49Z agramfor $
% $LastChangedBy: agramfor $
% $LastChangedDate: 2009-08-26 17:05:49 +0200 (Mer, 26 aoû 2009) $
% $Revision: 2 $
%
% 2015-07-22 Edited by Allison Hsiang: Turned off print statement for number of colors
% 2015-12-02 Edited by Allison Hsiang: Removed call to mesh_normals due to changes in Matlab R2015b, added 'normals' as input parameter

if nargin < 4
    face_vertex_data = [];
end

nfaces = size(faces,1);
npoints = size(points,1);
%normals = mesh_normals(points,faces,normals);

if ~isempty(face_vertex_data) && size(face_vertex_data,2) ~= 3
    error('IDTF colors should be RGB');
end
nface_vertex_data = size(face_vertex_data,1);

% if nface_vertex_data == npoints
%     if 0
%         face_vertex_data_mean = (face_vertex_data(faces(:,1),:)+face_vertex_data(faces(:,2),:)+ ...
%                                 face_vertex_data(faces(:,3),:))/3;
%         xx = face_vertex_data_mean - face_vertex_data(faces(:,1),:); xx = sum(xx.*xx,2);
%         yy = face_vertex_data_mean - face_vertex_data(faces(:,2),:); yy = sum(yy.*yy,2);
%         zz = face_vertex_data_mean - face_vertex_data(faces(:,3),:); zz = sum(zz.*zz,2);
%         [tmp,I] = sort([xx,yy,zz],2);
%         face_vertex_data = face_vertex_data(I(:,2),:);
%         % [tmp,I] = min([xx,yy,zz],[],2);
%         % face_vertex_data = face_vertex_data(I,:);
%     else
%         face_vertex_data = (face_vertex_data(faces(:,1),:)+face_vertex_data(faces(:,2),:)+ ...
%                             face_vertex_data(faces(:,3),:))/3;
%     end
%     nface_vertex_data = nfaces;
% end

fid = fopen(filename,'w');

if isempty(face_vertex_data)
    str = verbatim;
    %{
    FILE_FORMAT "IDTF"
    FORMAT_VERSION 100

    NODE "MODEL" {
         NODE_NAME "Mesh"
         PARENT_LIST {
              PARENT_COUNT 1
              PARENT 0 {
                   PARENT_NAME "<NULL>"
                   PARENT_TM {
                        1.000000 0.000000 0.000000 0.000000
                        0.000000 1.000000 0.000000 0.000000
                        0.000000 0.000000 1.000000 0.000000
                        0.000000 0.000000 0.000000 1.000000
                   }
              }
         }
         RESOURCE_NAME "MyMesh"
    }

    RESOURCE_LIST "MODEL" {
         RESOURCE_COUNT 1
         RESOURCE 0 {
              RESOURCE_NAME "MyMesh"
              MODEL_TYPE "MESH"
              MESH {
                   FACE_COUNT %d
                   MODEL_POSITION_COUNT %d
                   MODEL_NORMAL_COUNT %d
                   MODEL_DIFFUSE_COLOR_COUNT 0
                   MODEL_SPECULAR_COLOR_COUNT 0
                   MODEL_TEXTURE_COORD_COUNT 0
                   MODEL_BONE_COUNT 0
                   MODEL_SHADING_COUNT 1
                   MODEL_SHADING_DESCRIPTION_LIST {
                        SHADING_DESCRIPTION 0 {
                             TEXTURE_LAYER_COUNT 0
                             SHADER_ID 0
                        }
                   }
                   MESH_FACE_POSITION_LIST {
                        %s
                   }
                   MESH_FACE_NORMAL_LIST {
                        %s
                   }
                   MESH_FACE_SHADING_LIST {
                        0
                   }
                   MODEL_POSITION_LIST {
                        %s
                   }
                   MODEL_NORMAL_LIST {
                        %s
                   }
              }
         }
    }

    %}

    strfaces = sprintf('%d %d %d\n',faces'-1);
    strpoints = sprintf('%f %f %f\n',points');
    strnormals = sprintf('%f %f %f\n',normals');
    count = fprintf(fid,str,nfaces,npoints,npoints,strfaces,strfaces,strpoints,strnormals);

elseif nface_vertex_data == npoints

    [face_vertex_data_unique,tmp,face_vertex_data_idx] = unique(face_vertex_data, 'rows');
    nface_vertex_data_unique = size(face_vertex_data_unique,1);

    %disp(['nb of colors : ',num2str(nface_vertex_data_unique)]);

    str_with_colors = verbatim;
    %{
    FILE_FORMAT "IDTF"
    FORMAT_VERSION 100

    NODE "MODEL" {
         NODE_NAME "Mesh"
         PARENT_LIST {
              PARENT_COUNT 1
              PARENT 0 {
                   PARENT_NAME "<NULL>"
                   PARENT_TM {
                        1.000000 0.000000 0.000000 0.000000
                        0.000000 1.000000 0.000000 0.000000
                        0.000000 0.000000 1.000000 0.000000
                        0.000000 0.000000 0.000000 1.000000
                   }
              }
         }
         RESOURCE_NAME "MyMesh"
    }

    RESOURCE_LIST "MODEL" {
         RESOURCE_COUNT 1
         RESOURCE 0 {
              RESOURCE_NAME "MyMesh"
              MODEL_TYPE "MESH"
              MESH {
                   FACE_COUNT %d
                   MODEL_POSITION_COUNT %d
                   MODEL_NORMAL_COUNT 0
                   MODEL_DIFFUSE_COLOR_COUNT %d
                   MODEL_SPECULAR_COLOR_COUNT 0
                   MODEL_TEXTURE_COORD_COUNT 0
                   MODEL_BONE_COUNT 0
                   MODEL_SHADING_COUNT 1
                   MODEL_SHADING_DESCRIPTION_LIST {
                        SHADING_DESCRIPTION 0 {
                             TEXTURE_LAYER_COUNT 0
                             SHADER_ID 0
                        }
                   }
                   MESH_FACE_POSITION_LIST {
                        %s
                   }
                   MESH_FACE_SHADING_LIST {
                        %s
                   }
                   MESH_FACE_DIFFUSE_COLOR_LIST {
                        %s
                   }
                   MODEL_POSITION_LIST {
                        %s
                   }
                   MODEL_DIFFUSE_COLOR_LIST {
                    %s
                   }
              }
         }
    }

    RESOURCE_LIST "SHADER" {
         RESOURCE_COUNT 1
         RESOURCE 0 {
              RESOURCE_NAME "Box010"
              ATTRIBUTE_USE_VERTEX_COLOR "TRUE"
              SHADER_MATERIAL_NAME "Box010"
              SHADER_ACTIVE_TEXTURE_COUNT 0
         }
    }

    RESOURCE_LIST "MATERIAL" {
         RESOURCE_COUNT 1
         RESOURCE 0 {
              RESOURCE_NAME "Box010"
              MATERIAL_AMBIENT 0.0 0.0 0.0
              MATERIAL_DIFFUSE 1.0 1.0 1.0
              MATERIAL_SPECULAR 0.0 0.0 0.0
              MATERIAL_EMISSIVE 1.0 1.0 1.0
              MATERIAL_REFLECTIVITY 0.000000
              MATERIAL_OPACITY 1.000000
         }
    }

    MODIFIER "SHADING" {
         MODIFIER_NAME "Mesh"
         PARAMETERS {
              SHADER_LIST_COUNT 1
              SHADER_LIST_LIST {
                   SHADER_LIST 0 {
                        SHADER_COUNT 1
                        SHADER_NAME_LIST {
                             SHADER 0 NAME: "Box010"
                        }
                   }
              }
         }
    }

    %}

    strfaces = sprintf('%d %d %d\n',faces'-1);
    strfaces_colors = sprintf('%d %d %d\n',face_vertex_data_idx(faces)'-1);
    strpoints = sprintf('%f %f %f\n',points');
    strnormals = sprintf('%f %f %f\n',normals');
    strshading = sprintf('%d\n',zeros(nfaces,1));
    strcolors = sprintf('%f %f %f\n',face_vertex_data_unique');
    count = fprintf(fid,str_with_colors,nfaces,npoints,nface_vertex_data_unique,strfaces, ...
                    strshading,strfaces_colors,strpoints,strcolors);

else

    [face_vertex_data_unique,tmp,face_vertex_data_idx] = unique(face_vertex_data, 'rows');
    nface_vertex_data_unique = size(face_vertex_data_unique,1);

    str = verbatim;
    %{
    FILE_FORMAT "IDTF"
    FORMAT_VERSION 100

    NODE "MODEL" {
         NODE_NAME "Mesh"
         PARENT_LIST {
              PARENT_COUNT 1
              PARENT 0 {
                   PARENT_NAME "<NULL>"
                   PARENT_TM {
                        1.000000 0.000000 0.000000 0.000000
                        0.000000 1.000000 0.000000 0.000000
                        0.000000 0.000000 1.000000 0.000000
                        0.000000 0.000000 0.000000 1.000000
                   }
              }
         }
         RESOURCE_NAME "MyMesh"
    }

    RESOURCE_LIST "MODEL" {
         RESOURCE_COUNT 1
         RESOURCE 0 {
              RESOURCE_NAME "MyMesh"
              MODEL_TYPE "MESH"
              MESH {
                   FACE_COUNT %d
                   MODEL_POSITION_COUNT %d
                   MODEL_NORMAL_COUNT %d
                   MODEL_DIFFUSE_COLOR_COUNT 0
                   MODEL_SPECULAR_COLOR_COUNT 0
                   MODEL_TEXTURE_COORD_COUNT 0
                   MODEL_BONE_COUNT 0
                   MODEL_SHADING_COUNT %d
                   MODEL_SHADING_DESCRIPTION_LIST {
                    
    %}
    count = fprintf(fid,str,nfaces,npoints,npoints,nface_vertex_data_unique);

    idx = [0:(nfaces-1)]';
    shidx = [0:(nface_vertex_data_unique-1)]';
    str = verbatim;
    %{
                SHADING_DESCRIPTION %d {
                         TEXTURE_LAYER_COUNT 0
                         SHADER_ID %d
                    }
    
    %}
    count = fprintf(fid,str,[shidx,shidx]');

    str = verbatim;
    %{
                   }
                   MESH_FACE_POSITION_LIST {
                        %s
                   }
                   MESH_FACE_NORMAL_LIST {
                        %s
                   }
                   MESH_FACE_SHADING_LIST {
                        %s
                   }
                   MODEL_POSITION_LIST {
                        %s
                   }
                   MODEL_NORMAL_LIST {
                        %s
                   }
              }
         }
    }

    RESOURCE_LIST "SHADER" {
         RESOURCE_COUNT %d

    %}

    strfaces = sprintf('%d %d %d\n',faces'-1);
    strpoints = sprintf('%f %f %f\n',points');
    strnormals = sprintf('%f %f %f\n',normals');
    % stridx = sprintf('%d\n',idx);
    str_face_vertex_data_idx = sprintf('%d\n',face_vertex_data_idx-1);
    count = fprintf(fid,str,strfaces,strfaces,str_face_vertex_data_idx,strpoints,strnormals,nface_vertex_data_unique);

    str = verbatim;
    %{
         RESOURCE %d {
              RESOURCE_NAME "Box01%d"
              SHADER_MATERIAL_NAME "Box01%d"
              SHADER_ACTIVE_TEXTURE_COUNT 0
        }

    %}

    count = fprintf(fid,str,[shidx,shidx,shidx]');

    str = verbatim;
    %{
    }

    RESOURCE_LIST "MATERIAL" {
         RESOURCE_COUNT %d
    
    %}
    count = fprintf(fid,str,nface_vertex_data_unique);

    str = verbatim;
    %{
         RESOURCE %d {
              RESOURCE_NAME "Box01%d"
              MATERIAL_AMBIENT 0 0 0
              MATERIAL_DIFFUSE %f %f %f
              MATERIAL_SPECULAR 0.2 0.2 0.2
              MATERIAL_EMISSIVE 0 0 0
              MATERIAL_REFLECTIVITY 0.100000
              MATERIAL_OPACITY 1.000000
         }

    %}
    count = fprintf(fid,str,[shidx,shidx,face_vertex_data_unique]');

    str = verbatim;
    %{
    }

    MODIFIER "SHADING" {
         MODIFIER_NAME "Mesh"
         PARAMETERS {
              SHADER_LIST_COUNT %d
              SHADER_LIST_LIST {
    
    %}
    count = fprintf(fid,str,nface_vertex_data_unique);

    str = verbatim;
    %{
                   SHADER_LIST %d {
                        SHADER_COUNT 1
                        SHADER_NAME_LIST {
                             SHADER 0 NAME: "Box01%d"
                        }
                   }

    %}
    count = fprintf(fid,str,[shidx,shidx]');

    str = verbatim;
    %{
              }
         }
    }

    %}
    count = fprintf(fid,str);

end

fclose(fid);

end %  function
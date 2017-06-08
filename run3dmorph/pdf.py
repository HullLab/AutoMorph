#!/usr/bin/python

#Pipeline: Mesh -> IDTF -> U3D -> LaTeX -> 3D PDF

import textwrap
from sklearn.preprocessing import normalize
import platform
import os
import sys
import glob
import decimal
import shutil
import numpy as np
import subprocess
import time


def writeIDTF(obj,triangulation,triangles,faceColors):
    '''
    Writes 3D mesh into IDTF format for conversion to U3D format.
    '''
    faces = triangles
    vertices = triangulation.points
    #normals = meshNormals(faces,vertices)
    uniqueFaceColors = np.vstack(set([tuple(row) for row in faceColors]))

    numFaces = faces.shape[0]
    numVertices = vertices.shape[0]
    #numNormals = normals.shape[0]
    numColors = uniqueFaceColors.shape[0]

    # Match indices of unique face colors with list of face colors for
    # MESH_FACE_DIFFUSE_COLOR_LIST in IDTF file
    colorIdx = []
    colorDict = {}
    for i,faceColor in enumerate(uniqueFaceColors):
        colorDict[tuple(faceColor)] = i
    for color in faceColors:
        colorIdx.append(colorDict[tuple(color)])

    # Indices of vertices that make up faces
    meshFacePosition = '\n'.join(['{:d} {:d} {:d}'.format(face[0],face[1],face[2]) for face in faces])
    # Shading value for each face (all 0)
    meshFaceShading = '0\n' * numFaces
    # Color of indices for each face, given as index values corresponding to indices
    # of unique face colors
    meshFaceDiffuseColor = '\n'.join(['{:d} {:d} {:d}'.format(colorIdx[face[0]],colorIdx[face[1]],colorIdx[face[2]]) for face in faces])
    # Coordinates of all vertices
    modelPosition = '\n'.join(['{0:.{1}f} {2:.{3}f} {4:.{5}f}'.format(vertex[0],3,vertex[1],3,vertex[2],3) for vertex in vertices])
    # RGB values for all unique face colors (in order of indices passed to meshFaceDiffuseColor)
    modelDiffuseColor = '\n'.join(['{:f} {:f} {:f}'.format(color[0],color[1],color[2]) for color in uniqueFaceColors])

    text = textwrap.dedent('''
            FILE_FORMAT "IDTF"
            FORMAT_VERSION 100

            NODE "MODEL" {{
                 NODE_NAME "Mesh"
                 PARENT_LIST {{
                      PARENT_COUNT 1
                      PARENT 0 {{
                           PARENT_NAME "<NULL>"
                           PARENT_TM {{
                                1.000000 0.000000 0.000000 0.000000
                                0.000000 1.000000 0.000000 0.000000
                                0.000000 0.000000 1.000000 0.000000
                                0.000000 0.000000 0.000000 1.000000
                           }}
                      }}
                 }}
                 RESOURCE_NAME "MyMesh"
            }}

            RESOURCE_LIST "MODEL" {{
                 RESOURCE_COUNT 1
                 RESOURCE 0 {{
                      RESOURCE_NAME "MyMesh"
                      MODEL_TYPE "MESH"
                      MESH {{
                           FACE_COUNT {:d}
                           MODEL_POSITION_COUNT {:d}
                           MODEL_NORMAL_COUNT 0
                           MODEL_DIFFUSE_COLOR_COUNT {:d}
                           MODEL_SPECULAR_COLOR_COUNT 0
                           MODEL_TEXTURE_COORD_COUNT 0
                           MODEL_BONE_COUNT 0
                           MODEL_SHADING_COUNT 1
                           MODEL_SHADING_DESCRIPTION_LIST {{
                                SHADING_DESCRIPTION 0 {{
                                     TEXTURE_LAYER_COUNT 0
                                     SHADER_ID 0
                                }}
                           }}
                           MESH_FACE_POSITION_LIST {{
                                {:s}
                           }}
                           MESH_FACE_SHADING_LIST {{
                                {:s}
                           }}
                           MESH_FACE_DIFFUSE_COLOR_LIST {{
                                {:s}
                           }}
                           MODEL_POSITION_LIST {{
                                {:s}
                           }}
                           MODEL_DIFFUSE_COLOR_LIST {{
                                {:s}
                           }}
                      }}
                 }}
            }}

            RESOURCE_LIST "SHADER" {{
                 RESOURCE_COUNT 1
                 RESOURCE 0 {{
                      RESOURCE_NAME "Box010"
                      ATTRIBUTE_USE_VERTEX_COLOR "TRUE"
                      SHADER_MATERIAL_NAME "Box010"
                      SHADER_ACTIVE_TEXTURE_COUNT 0
                 }}
            }}

            RESOURCE_LIST "MATERIAL" {{
                 RESOURCE_COUNT 1
                 RESOURCE 0 {{
                      RESOURCE_NAME "Box010"
                      MATERIAL_AMBIENT 0.0 0.0 0.0
                      MATERIAL_DIFFUSE 1.0 1.0 1.0
                      MATERIAL_SPECULAR 0.0 0.0 0.0
                      MATERIAL_EMISSIVE 1.0 1.0 1.0
                      MATERIAL_REFLECTIVITY 0.000000
                      MATERIAL_OPACITY 1.000000
                 }}
            }}

            MODIFIER "SHADING" {{
                 MODIFIER_NAME "Mesh"
                 PARAMETERS {{
                      SHADER_LIST_COUNT 1
                      SHADER_LIST_LIST {{
                           SHADER_LIST 0 {{
                                SHADER_COUNT 1
                                SHADER_NAME_LIST {{
                                     SHADER 0 NAME: "Box010"
                                }}
                           }}
                      }}
                 }}
            }}
    ''')

    with open(obj.idtf,'wb') as idtf:
        idtf.write(text.format(numFaces,numVertices,numColors,meshFacePosition,meshFaceShading,meshFaceDiffuseColor,modelPosition,modelDiffuseColor))


def convertU3D(obj,run3dmorphPath):
    '''
    Calls IDTFConverter to convert IDTF file to U3D format.
    '''
    sysName = platform.system()

    if sysName == 'Linux':
        executable = './IDTFConverter.sh'
        idtfcPath = os.path.join(run3dmorphPath,'lib','IDTFConverter','glx')
    elif sysName == 'Darwin':
        executable = './IDTFConverter'
        idtfcPath = os.path.join(run3dmorphPath,'lib','IDTFConverter','maci')
    elif sysName == 'Windows':
        executable = './IDTFConverter.exe'
        idtfcPath = os.path.join(run3dmorphPath,'lib','IDTFConverter','w32')
    else:
        print 'INFO: IDTFConverter not available for your system.'
        sys.exit('INFO: Cannot create 3D PDFs. Exiting...')

    os.chdir(idtfcPath)

    call = [executable,'-input',obj.idtf,'-output',obj.u3d]
    # Suppress call output by redirecting output to DEVNULL
    FNULL = open(os.devnull,'w')
    subprocess.call(call,stdout=FNULL,stderr=subprocess.STDOUT)


def convertJPG(obj):
    '''
    Converts focused_unlabeled/rgb images and stripped/label labels from
    TIF to JPG format for LaTeX PDF generation.
    '''
    rgbCall = ['convert',obj.rgb,obj.rgbJPG]
    labelCall = ['convert',obj.label,obj.labelJPG]
    # Suppress call output by redirecting output to DEVNULL
    FNULL = open(os.devnull,'w')
    subprocess.call(rgbCall,stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(labelCall,stdout=FNULL,stderr=subprocess.STDOUT)


def writeLatexFile(settings,obj,run3dmorphPath,length,width):
    '''
    Writes LaTeX file for 3D PDF generation.
    '''
    with open(obj.latex,'wb') as latex:
        text = textwrap.dedent('''
                \documentclass{{article}}
                \usepackage{{{:s}}}
                \usepackage[colorlinks=true]{{hyperref}}
                \usepackage{{siunitx}}

                \setlength{{\\voffset}}{{-0.75in}}
                \setlength{{\headsep}}{{5pt}}
                \setlength{{\intextsep}}{{5pt}}
                \setlength{{\\textfloatsep}}{{-1pt}}
                \setlength{{\\textheight}}{{650pt}}

                \\begin{{document}}
                \pagestyle{{empty}}

                \\begin{{figure}}[t]
                	\centerline{{\includegraphics[scale=0.5]{{{:s}}}}}
                \end{{figure}}

                \\begin{{center}}
                	Length: \SI{{{:f}}} - Width: \SI{{{:f}}} - Grid Size: \SI{{{:d}}} - Unit: {:s}\end{{center}}

                \centerline{{\includemedia[
                label={:s},
                width=1\linewidth,height=1\linewidth,
                playbutton=none,
                activate=pageopen,
                3Dlights=CAD,
                3Daac=7,
                3Droll=0,
                3Dc2c=-4 -2 5,
                3Droo=85,
                3Dcoo=6 4 0
                ]{{}}{{{:s}}}}}

                \\begin{{figure}}[b]
                	\centerline{{\includegraphics[scale=0.2]{{{:s}}}}}
                \end{{figure}}

                \end{{document}}
                ''')

        media9Path = os.path.abspath(os.path.join(run3dmorphPath,'lib','media9','media9'))
        labelPath = os.path.splitext(obj.labelJPG)[0]
        length = float(round(decimal.Decimal(length),3))
        width = float(round(decimal.Decimal(width),3))
        rgbPath = os.path.splitext(obj.rgbJPG)[0]

        latex.write(text.format(media9Path,labelPath,length,width,settings['grid_size'],settings['unit'],obj.u3d,obj.u3d,rgbPath))


def runLatex(obj):
    '''
    Runs LaTeX to generate 3D PDF.
    '''
    call = ['pdflatex','-output-directory',obj.pdf,obj.latex]
    # Suppress call output by redirecting output to DEVNULL
    FNULL = open(os.devnull,'w')
    # Note that pdflatex must be added to /usr/local/bin for this to work
    subprocess.call(call,stdout=FNULL,stderr=subprocess.STDOUT)
    # Clean up (removes auxiliary LaTeX files after run)
    toDelete = [f for f in glob.glob(os.path.join(obj.pdf,'*')) if not os.path.splitext(f)[1] == '.pdf']
    for f in toDelete:
        os.remove(f)


def makePDF(settings,obj,run3dmorphPath,triangulation,triangles,faceColors,length,width):
    '''
    Pipeline for 3D PDF generation.
    '''
    start = time.time()

    os.environ['PATH'] += os.pathsep + '/usr/local/bin'

    # Write mesh in IDTF format
    writeIDTF(obj,triangulation,triangles,faceColors)
    # Convert IDTF file to U3D format
    convertU3D(obj,run3dmorphPath)
    # Convert RGB and label to JPG format
    convertJPG(obj)
    # Write LaTeX file
    writeLatexFile(settings,obj,run3dmorphPath,length,width)
    # Run LaTeX to generate 3D PDF
    runLatex(obj)

    end = time.time()
    time_elapsed = end - start
    print '\tINFO: Time elapsed: {:.3f} seconds\n'.format(time_elapsed)


# def newellNormal(vertices):
#     '''
#     Vertices are those that define the surface for which we want
#     to calculate a normal.
#
#     Returns normal of arbitrary 3D polygon, calculated using Newell's
#     method, as a Numpy array.
#     '''
#     normal = [0.0, 0.0, 0.0]
#
#     for i,v in enumerate(vertices):
#         v_next = vertices[(i + 1) % len(vertices)] # Modulo allows for end-wrapping of array indices
#         normal[0] += (v[1] - v_next[1]) * (v[2] + v_next[2]) # (Y_0 - Y_1) * (Z_0 + Z_1)
#         normal[1] += (v[2] - v_next[2]) * (v[0] + v_next[0]) # (Z_0 - Z_1) * (X_0 + X_1)
#         normal[2] += (v[0] - v_next[0]) * (v[1] + v_next[1]) # (X_0 - X_1) * (Y_0 + Y_1)
#
#     # Reshape necessary to avoid deprecation warning in sklearn
#     return normalize(np.array(normal).reshape(1,-1))
#
#
# def meshNormals(faces,vertices):
#     # Initialize Numpy array for normals
#     normals = np.empty((faces.shape[0],3))
#
#     # Loop through face polygons and calculate normals
#     for i,face in enumerate(faces):
#         faceVertices = [vertices[v] for v in face]
#         normals[i] = newellNormal(faceVertices)
#
#     return normals

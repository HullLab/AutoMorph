#!/usr/bin/env python

import os
import time


def saveOBJOFF(settings,obj,triangulation):
    '''
    Converts mesh to OBJ and OFF format and saves them as individual files.
    '''
    start = time.time()

    vertices = triangulation.points
    faces = triangulation.simplices
    numVertices = len(vertices)
    numFaces = len(faces)

    with open(obj.off,'wb') as off_f, open(obj.obj,'wb') as obj_f:
        # Write headers with object name
        off_f.write('OFF\n# {:s}\n\n{:s} {:s} 0\n'.format(os.path.basename(obj.off),str(numVertices),str(numFaces)))
        obj_f.write('# {:s}\n\n'.format(os.path.basename(obj.obj)))
        # Write vertices
        for v in vertices:
            vw = ' '.join([str(v[0]),str(v[1]),str(v[2])])
            off_f.write('{:s}\n'.format(vw))
            obj_f.write('v {:s}\n'.format(vw))
        # Write faces
        for f in faces:
            indices = [str(f[0]),str(f[1]),str(f[2]),str(f[3])]
            fw = ' '.join(indices)
            off_f.write('{:d} {:s}\n'.format(len(indices),fw))
            obj_f.write('f {:s}\n'.format(fw))

    end = time.time()
    time_elapsed = end - start
    print '\tINFO: Time elapsed: {:.3f} seconds\n'.format(time_elapsed)

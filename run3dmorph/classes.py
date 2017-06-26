#!/usr/bin/python

import os
import sys

class Object:
    'Class for identified individual objects'
    total = 0

    def __init__(self,obj,settings,num):
        self.sid = settings['sampleID']
        self.num = num
        self.numStr = 'obj' + (5 - len(str(self.num))) * '0' + str(self.num)
        self.name = obj
        self.latexName = self.name.replace('.','_')

        # Input paths and extensions
        self.rgb = os.path.join(settings['in_directory'],'focused_unlabeled','.'.join([self.name,'tif']))
        self.rgbJPG = os.path.join(os.path.dirname(self.rgb),'.'.join([self.latexName,'jpg']))
        self.stack = os.path.join(settings['in_directory'],'stripped',self.name)
        self.stackExt = '.' + settings['stack_image_ext'] if '.' not in settings['stack_image_ext'] else settings['stack_image_ext']
        self.label = os.path.join(settings['in_directory'],'stripped','labels','.'.join([self.name,'tif']))
        self.labelJPG = os.path.join(settings['in_directory'],'stripped','labels','.'.join([self.latexName,'jpg']))

        # Output paths
        self.morph3d = os.path.join(settings['out_directory'],'morph3d') # Directory
        # ImageJ
        self.macro = os.path.join(self.morph3d,'heightmaps','macros','.'.join(['_'.join([self.name,'macro']),'imj']))
        self.fijiFocused = os.path.join(self.morph3d,'heightmaps','FIJI_focused','.'.join(['_'.join([self.name,'fiji_focused']),'tif']))
        self.heightmap = os.path.join(self.morph3d,'heightmaps','.'.join(['_'.join([self.name,'heightmap']),'tif']))
        # Measurements
        self.volume = os.path.join(self.morph3d,'volumes','.'.join(['_'.join([self.name,'volume_surface_area']),'csv']))
        # 3D mesh
        self.off = os.path.join(self.morph3d,'offs','.'.join([self.name,'off']))
        self.obj = os.path.join(self.morph3d,'objs','.'.join([self.name,'obj']))
        self.coordinates = os.path.join(self.morph3d,'coordinates','.'.join(['_'.join([self.name,'coordinates']),'csv']))
        # PDF
        self.pdf = os.path.join(self.morph3d,'pdfs','pdf') # Directory
        self.idtf = os.path.join(self.morph3d,'pdfs','idtf','.'.join([self.name,'idtf'])) # File
        self.u3d = os.path.join(self.morph3d,'pdfs','u3d','.'.join([self.latexName,'u3d'])) # File
        self.latex = os.path.join(self.morph3d,'pdfs','latex','.'.join([self.name,'tex'])) # File

        Object.total += 1

    def showTotal(self):
        print 'INFO: Total number of objects found: {:d}\n'.format(Object.total)

    def showObject(self):
        print 'INFO: Current object: {:s}'.format(self.name)

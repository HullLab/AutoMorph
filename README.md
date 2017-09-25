AutoMorph
=========

Automated Morphometrics: image segmentation, 2D and 3D shape extraction, classification, and analysis.

Python Prerequisites
-------------

* python (2.7)
* scikit-learn
* scikit-image (v0.9.0+)
* scipy
* numpy
* pillow
* tifffile
* pandas
* matplotlib
* opencv
* shapely

The easiest way to get most of these Python modules is to just install [Anaconda](https://www.continuum.io/downloads).

To get the tifffile, opencv, and shapely modules, you can simply install them into your Anaconda installation like so:

    $ conda install tifffile -c conda-forge
    $ conda install opencv -c conda-forge
    $ conda install shapely

You may run into the following error message when running AutoMorph:

    ImportError: libopenblas.so.0: cannot open shared object file: No such file or directory

In this situation, you should install Openblas as well:

    $ conda install openblas

Finally, if you choose to install the packages manually instead of using Anaconda, note that
scikit-learn and scikit-image and called sklearn and skimage, respectively, in Python
repositories.


Additional Prerequisites
-------------

* FIJI or Zerene Stacker
* LaTeX
* ImageMagick

Details about these prerequisites and installation can be found in the provided manuals.


Installation
------------

Detailed installation instructions are found in the manuals. In general, you can create symbolic links for the AutoMorph executables like so:

    $ ln -s ${AUTOMORPH_DIR}/segment/segment /usr/local/bin
    $ ln -s ${AUTOMORPH_DIR}/focus/focus /usr/local/bin
    $ ln -s ${AUTOMORPH_DIR}/run2dmorph/run2dmorph /usr/local/bin
    $ ln -s ${AUTOMORPH_DIR}/run3dmorph/run3dmorph /usr/local/bin

Or, you can edit the 'rc' files (bashrc / cshrc, depending on shell) to add AutoMorph to your path. There are lines that look like (bashrc version):

    export PATH=${PATH}:${AUTOMORPH_DIR}/segment
    export PATH=${PATH}:${AUTOMORPH_DIR}/focus
    export PATH=${PATH}:${AUTOMORPH_DIR}/run2dmorph
    export PATH=${PATH}:${AUTOMORPH_DIR}/run3dmorph
    export PATH=${PATH}:${AUTOMORPH_DIR}/run3dmorph/lib
    export PATH=${PATH}:${AUTOMOPRH_DIR}/utilities

In either case, fix the '${AUTOMORPH_DIR}/' bit so that it uses the path you've copied these files into (eg, '/home/me/automorph')



Usage
-----

Please refer to the manuals for more detailed explanations of usage and parameters.

### segment

Copy segment/segment_control_file_v2017-06.txt to a directory of your chosing and configure for your run.

Use segment as:

    $ segment <control_file>

If run in 'sample' mode, segment will create a 'sample' directory containing an overview jpg of the full slide with numbered boxes around identified objects. One jpg will be created for each threshold setting in range specified.

If run in 'final' mode, segment will create a 'final' directory containing an overview jpg of the full slide with numbered boxes around identified objects and a directory of images for each object.


### focus

Edit focus/focus.cfg to use your software of choice (zerene for Zerene Stacker or fiji for FIJI).

Use focus as (<directory_path> = directory you want to run focus on):

    $ focus <directory_path>

Focus will move the original segmented files to z.stacks/ and (if run sucessfully) the final images can be found in focused/.

Focus can be run with the following optional flags:

-v, --verbose : increases the verbosity of focus, in particular it will print the zerene.log to the screen as ZereneStacker runs. May cause ZereneStacker to run more slowly.

-i, --interactive : runs focusing software with headless mode turned off, to be used if the software isn't running properly. Use only for debugging, since interactive mode severely affects performance.

--reset : will reset the input directory to a pre-focused state, to be used if focus fails for some reason or you want to rerun

##### Using focus with ZereneStacker

Change zerene_dir in focus/focus.cfg to reflect the location of the Zerene Stacker software (and it's executable script) on your system.


### run2dmorph

Copy run2dmorph/run2dmorph_control_file_v2017-06.txt to a directory of your chosing and configure for your run.

Use run2dmorph as:

    $ run2dmorph <control_file>


### run3dmorph

Copy run3dmorph/run3dmorph_control_file_v2017-06.txt to a directory of your chosing and configure for your run.

Use run3dmorph as:

    $ run3dmorph <control_file>

Run3dmorph can be run with the following optional flags:

--reset : removes any previous run3dmorph output present in the specified output directory

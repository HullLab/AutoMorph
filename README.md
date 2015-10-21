AutoMorph
=========

Automated Morphometrics: image segmentation, 2D and 3D shape extraction, classification, and analysis.

Prerequisites
-------------

* python (2.7)
* scikit-learn
* scipy
* numpy
* pillow

Easiest way to get these python modules is to just install [Anaconda](https://www.continuum.io/downloads).

You also need a copy of the Zerene Stacker software to run the focus step.


Installation
------------

Edit the 'rc' files (bashrc / cshrc, depending on shell)

There are lines that look like (bashrc version):

    export PATH=${PATH}:${AUTOMORPH_DIR}/segment
    export PATH=${PATH}:${AUTOMORPH_DIR}/focus
    export PATH=${PATH}:${AUTOMORPH_DIR}/run2dmorph/bin

Fix the '${AUTOMORPH_DIR}/' bit so that it uses the path you've copied these files into (eg, '/home/me/automorph')


Usage
-----

### segment

Copy segment/python/example_settings.txt to a directory of your chosing and configure for your run.

Use segment as:

    $ segment <settings_file>

If run in 'sample' mode, segment will create a 'sample' directory containing an overview jpg of the full slide with numbered boxes around identified objects. One jpg will be created for each threshold setting in range specified.

If run in 'final' mode, segment will create a 'final' directory containing an overview jpg of the full slide with numbered boxes around identified objects and a directory of images for each object.


### focus

Edit focus/focus.cfg to use your software of choice (zerene is only available options at the moment)

Use focus as (<directory_path> = directory you want to run focus on):

    $ focus <directory_path>

Focus will move the original segmented files to z.stacks/ and (if run sucessfully) the final images can be found in focused/.

Focus can be run with the following optional flags:

-v, --verbose : increases the verbosity of focus, in particular it will print the zerene.log to the screen as ZereneStacker runs. May cause ZereneStacker to run more slowly.

-i, --interactive: runs focusing software with headless mode turned off, to be used if the software isn't running properly. Use only for debugging, since interactive mode severely affects performance.

--reset : will reset the input directory to a pre-focused state, to be used if focus fails for some reason or you want to rerun

##### Using focus with ZereneStacker

Change zerene_dir in focus/focus.cfg to reflect the location of the Zerene Stacker software (and it's executable script) on your system.



### run2dmorph

Documentation coming soon.

import platform
import os
import glob
import pwd


def run(directories, software):

    # Initialize the batch XML file
    write_batchfile(directories)

    # Run the XML file
    zerene_command = construct_command(software)
    if software['verbose']:
        zerene_command += ' %s 2>&1 | tee %s' % (os.path.join(directories['input'], 'zsbatch.xml'),
                                                 os.path.join(directories['input'], 'zerene.log'))
    else:
        zerene_command += ' %s > %s' % (os.path.join(directories['input'], 'zsbatch.xml'),
                                        os.path.join(directories['input'], 'zerene.log'))
    print 'Running Zerene Stacker: ', zerene_command

    subprocess.call(zerene_command, shell=True)

    first_object = os.path.realpath(os.path.join(directories['stripped'],
                                                 os.path.basename(directories["objects"][0]),
                                                 'ZS.tif'))
    last_object = os.path.realpath(os.path.join(directories['stripped'],
                                                os.path.basename(directories["objects"][-1]),
                                                'ZS.tif'))

    if not os.path.exists(first_object):
        sys.exit("Error: Zerene didn't create files. Perhaps something went wrong? Exiting...")
    elif not os.path.exists(last_object):
        sys.exit("Error: Zerene didn't finish creating files. Perhaps something went wrong? Exiting...")
    else:
        print 'Zerene Stacker finished!'

def construct_command(software):

    zerene_dir = software['zerene_dir']
    systemMemoryMB = software['system_memory_MB']
    temp_dir = software['temp_dir']
    if 'headless' in software.keys():
        headless = software['headless']
    else:
        headless = ''

    zerene_java_options = "-Xmx%sm -Djava.io.tmpDir=%s" % (systemMemoryMB,
                                                           os.path.join(temp_dir, pwd.getpwuid(os.getuid()).pw_name)+'_ZereneStacker')
    zerene_java_extensions = ['jai_codec.jar', 'jai_core.jar', 'jai_imageio.jar',
                              'jdom.jar', 'metadata-extractor-2.4.0-beta-1.jar']
    zerene_options = "com.zerenesystems.stacker.gui.MainFrame -exitOnBatchScriptCompletion"
    if headless != '':
        zerene_options += " -runMinimized"
    zerene_options += " -noSplashScreen -showProgressWhenMinimized=false  -batchScript"

    if platform.system() == 'Darwin':
        print 'Configuring for Mac OS X'
        # Set up the Zerene Variables for Mac OS X:
        zerene_java = '/usr/bin/java'
        zerene_class_path = '-classpath ' + os.path.join(zerene_dir, 'Contents/Resources/Java', 'ZereneStacker.jar')
        for extension in zerene_java_extensions:
            zerene_class_path = zerene_class_path + ':' + os.path.join(zerene_dir, 'Contents/Resources/Java', extension)

    else:
        # Set up the Zerene Variables for Linux:
        print 'Configuring for Linux'
        zerene_java = os.path.join(zerene_dir, 'jre', 'bin', 'java')
        zerene_java_extensions.append('AppleShell.jar')
        zerene_class_path = '-classpath ' + os.path.join(zerene_dir, 'ZereneStacker.jar')
        for extension in zerene_java_extensions:
            zerene_class_path = zerene_class_path + ':' + os.path.join(zerene_dir, 'JREextensions', extension)

    zerene_command = ' '.join([headless, zerene_java, zerene_java_options, zerene_class_path, zerene_options])

    return zerene_command




def write_batchfile(directories, batch_type="default"):

    batchxml_object = set_batchxml(batch_type)

    batchxml_header = """<?xml version="1.0" encoding="UTF-8"?>
    <ZereneStackerBatchScript>
      <WrittenBy value="Zerene Stacker 1.04 Build T201404082055" />
          <BatchQueue>
                <Batches length="{0}">
                      """.format(len(directories['objects']))

    batchxml_footer = """
        </Batches>
      </BatchQueue>
    </ZereneStackerBatchScript>
                      """

    # Step 4: Loop over all object directories and write the ZereneStacker batch XML file:
    with open(os.path.join(directories["input"], 'zsbatch.xml'), 'w') as zsbatch:

        zsbatch.write(batchxml_header)

        stripped_objects = [os.path.realpath(x) for x in glob.glob(os.path.join(directories["stripped"], '*_obj*'))]

        for stripped_object in stripped_objects:
            print 'Adding object to batch file: ', stripped_object
            zsbatch.write(batchxml_object.format(stripped_object, directories["input"]))

        zsbatch.write(batchxml_footer)
        print 'Batch XML file written.'


def set_batchxml(batch_type):

    if batch_type == "DMAP":
        batchxml_object = """
          <Batch>
            <Sources length="1">
              <Source value="{0}" />
            </Sources>
            <ProjectDispositionCode value="101" />
            <Tasks length="1">
              <Task>
                <OutputImageDispositionCode value="2" />
                <OutputImagesDesignatedFolder value="{1}/focused/" />
                <Preferences>
                  <AcquisitionSequencer.BacklashMillimeters value="0.22" />
                  <AcquisitionSequencer.CommandLogging value="false" />
                  <AcquisitionSequencer.DistancePerStepperRotation value="1.5875" />
                  <AcquisitionSequencer.MaximumMmPerSecond value="2.0" />
                  <AcquisitionSequencer.MicrostepsPerRotation value="3200" />
                  <AcquisitionSequencer.MovementRampTime value="2.0" />
                  <AcquisitionSequencer.NumberOfSteps value="5" />
                  <AcquisitionSequencer.PrecisionThreshold value="0.05" />
                  <AcquisitionSequencer.PrerunMillimeters value="0.0" />
                  <AcquisitionSequencer.RPPIndicatorLeft value="-100.0" />
                  <AcquisitionSequencer.RPPIndicatorRight value="+100.0" />
                  <AcquisitionSequencer.SettlingTime value="3.0" />
                  <AcquisitionSequencer.ShutterActivationsPerStep value="1" />
                  <AcquisitionSequencer.ShutterAfterTime value="2.0" />
                  <AcquisitionSequencer.ShutterBetweenTime value="1.0" />
                  <AcquisitionSequencer.ShutterPulseTime value="0.3" />
                  <AcquisitionSequencer.StepSize value="0.1" />
                  <AcquisitionSequencer.StepSizeAdjustmentFactor value="1.0" />
                  <AcquisitionSequencer.StepSizesFile value="" />
                  <AlignmentControl.AddNewFilesAsAlreadyAligned value="false" />
                  <AlignmentControl.AlignmentSettingsChanged value="false" />
                  <AlignmentControl.BrightnessSettingsChanged value="false" />
                  <AlignmentControl.MaxRelDegRotation value="20" />
                  <AlignmentControl.MaxRelPctScale value="20" />
                  <AlignmentControl.MaxRelPctShiftX value="20" />
                  <AlignmentControl.MaxRelPctShiftY value="20" />
                  <AlignmentControl.Order.Automatic value="true" />
                  <AlignmentControl.Order.NarrowFirst value="true" />
                  <AllowReporting.UsageStatistics value="false" />
                  <ColorManagement.DebugPrintProfile value="false" />
                  <ColorManagement.InputOption value="Use_EXIF_and_DCF_rules" />
                  <ColorManagement.InputOption.AssumedProfile value="sRGB IEC61966-2.1" />
                  <ColorManagement.ManageZSDisplays value="false" />
                  <ColorManagement.ManageZSDisplaysHasChanged value="false" />
                  <ColorManagement.OutputOption value="CopyInput" />
                  <DepthMapControl.AlgorithmIdentifier value="1" />
                  <DepthMapControl.ContrastThresholdLevel value="0" />
                  <DepthMapControl.ContrastThresholdPercentile value="25.0" />
                  <DepthMapControl.EstimationRadius value="10" />
                  <DepthMapControl.SaveDepthMapImage value="false" />
                  <DepthMapControl.SaveDepthMapImageDirectory value="" />
                  <DepthMapControl.SaveUsedPixelImages value="false" />
                  <DepthMapControl.SmoothingRadius value="5" />
                  <DepthMapControl.UseFixedContrastThresholdLevel value="false" />
                  <DepthMapControl.UseFixedContrastThresholdPercentile value="true" />
                  <DepthMapControl.UsedPixelFractionThreshold value="0.5" />
                  <FileIO.UseExternalTIFFReader value="false" />
                  <Interpolator.RenderingSelection value="Interpolator.Spline4x4" />
                  <Interpolator.ShowAdvanced value="false" />
                  <LightroomPlugin.CurrentInstallationFolder value="" />
                  <LightroomPlugin.DefaultColorSpace value="AdobeRGB" />
                  <OutputImageNaming.Template value="ZS" />
                  <Precrop.LimitsString value="" />
                  <Precrop.Selected value="false" />
                  <Prerotation.Degrees value="0" />
                  <Prerotation.Selected value="false" />
                  <Presize.UserSetting.Scale value="1.0" />
                  <Presize.UserSetting.Selected value="false" />
                  <Presize.Working.Scale value="1.0" />
                  <PyramidControl.GritSuppressionMethod value="1" />
                  <PyramidControl.RetainUDRImage value="false" />
                  <RetouchingBrush.Hardness value="0.5" />
                  <RetouchingBrush.ShowBrushes value="false" />
                  <RetouchingBrush.Type value="Details" />
                  <RetouchingBrush.Width value="10" />
                  <SaveImage.BitsPerColor value="8" />
                  <SaveImage.CompressionQuality value="1.00" />
                  <SaveImage.FileType value="tif" />
                  <SaveImage.RescaleImageToAvoidOverflow value="false" />
                  <SkewSequence.FirstImage.MaximumShiftXPct value="-3.0" />
                  <SkewSequence.FirstImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.LastImage.MaximumShiftXPct value="3.0" />
                  <SkewSequence.LastImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.NumberOfOutputImages value="3" />
                  <SkewSequence.Selected value="false" />
                  <StackingControl.FrameSkipFactor value="1" />
                  <StackingControl.FrameSkipSelected value="false" />
                  <StereoOrdering.LeftRightIndexSeparation value="1" />
                  <WatchDirectoryOptions.AcceptViaDelay value="false" />
                  <WatchDirectoryOptions.AcceptViaDelaySeconds value="2.0" />
                </Preferences>
                <TaskIndicatorCode value="2" />
              </Task>
            </Tasks>
          </Batch>
    """

    elif batch_type == "PMAX":
        batchxml_object = """
          <Batch>
            <Sources length="1">
              <Source value="{0}" />
            </Sources>
            <ProjectDispositionCode value="101" />
            <Tasks length="1">
              <Task>
                <OutputImageDispositionCode value="2" />
                <OutputImagesDesignatedFolder value="{1}/focused/" />
                <Preferences>
                  <AcquisitionSequencer.BacklashMillimeters value="0.22" />
                  <AcquisitionSequencer.CommandLogging value="false" />
                  <AcquisitionSequencer.DistancePerStepperRotation value="1.5875" />
                  <AcquisitionSequencer.MaximumMmPerSecond value="2.0" />
                  <AcquisitionSequencer.MicrostepsPerRotation value="3200" />
                  <AcquisitionSequencer.MovementRampTime value="2.0" />
                  <AcquisitionSequencer.NumberOfSteps value="5" />
                  <AcquisitionSequencer.PrecisionThreshold value="0.05" />
                  <AcquisitionSequencer.PrerunMillimeters value="0.0" />
                  <AcquisitionSequencer.RPPIndicatorLeft value="-100.0" />
                  <AcquisitionSequencer.RPPIndicatorRight value="+100.0" />
                  <AcquisitionSequencer.SettlingTime value="3.0" />
                  <AcquisitionSequencer.ShutterActivationsPerStep value="1" />
                  <AcquisitionSequencer.ShutterAfterTime value="2.0" />
                  <AcquisitionSequencer.ShutterBetweenTime value="1.0" />
                  <AcquisitionSequencer.ShutterPulseTime value="0.3" />
                  <AcquisitionSequencer.StepSize value="0.1" />
                  <AcquisitionSequencer.StepSizeAdjustmentFactor value="1.0" />
                  <AcquisitionSequencer.StepSizesFile value="" />
                  <AlignmentControl.AddNewFilesAsAlreadyAligned value="false" />
                  <AlignmentControl.AlignmentSettingsChanged value="false" />
                  <AlignmentControl.BrightnessSettingsChanged value="false" />
                  <AlignmentControl.MaxRelDegRotation value="20" />
                  <AlignmentControl.MaxRelPctScale value="20" />
                  <AlignmentControl.MaxRelPctShiftX value="20" />
                  <AlignmentControl.MaxRelPctShiftY value="20" />
                  <AlignmentControl.Order.Automatic value="true" />
                  <AlignmentControl.Order.NarrowFirst value="true" />
                  <AllowReporting.UsageStatistics value="false" />
                  <ColorManagement.DebugPrintProfile value="false" />
                  <ColorManagement.InputOption value="Use_EXIF_and_DCF_rules" />
                  <ColorManagement.InputOption.AssumedProfile value="sRGB IEC61966-2.1" />
                  <ColorManagement.ManageZSDisplays value="false" />
                  <ColorManagement.ManageZSDisplaysHasChanged value="false" />
                  <ColorManagement.OutputOption value="CopyInput" />
                  <DepthMapControl.AlgorithmIdentifier value="1" />
                  <DepthMapControl.ContrastThresholdLevel value="0" />
                  <DepthMapControl.ContrastThresholdPercentile value="25.0" />
                  <DepthMapControl.EstimationRadius value="10" />
                  <DepthMapControl.SaveDepthMapImage value="false" />
                  <DepthMapControl.SaveDepthMapImageDirectory value="" />
                  <DepthMapControl.SaveUsedPixelImages value="false" />
                  <DepthMapControl.SmoothingRadius value="5" />
                  <DepthMapControl.UseFixedContrastThresholdLevel value="false" />
                  <DepthMapControl.UseFixedContrastThresholdPercentile value="true" />
                  <DepthMapControl.UsedPixelFractionThreshold value="0.5" />
                  <FileIO.UseExternalTIFFReader value="false" />
                  <Interpolator.RenderingSelection value="Interpolator.Spline4x4" />
                  <Interpolator.ShowAdvanced value="false" />
                  <LightroomPlugin.CurrentInstallationFolder value="" />
                  <LightroomPlugin.DefaultColorSpace value="AdobeRGB" />
                  <OutputImageNaming.Template value="ZS" />
                  <Precrop.LimitsString value="" />
                  <Precrop.Selected value="false" />
                  <Prerotation.Degrees value="0" />
                  <Prerotation.Selected value="false" />
                  <Presize.UserSetting.Scale value="1.0" />
                  <Presize.UserSetting.Selected value="false" />
                  <Presize.Working.Scale value="1.0" />
                  <PyramidControl.GritSuppressionMethod value="1" />
                  <PyramidControl.RetainUDRImage value="false" />
                  <RetouchingBrush.Hardness value="0.5" />
                  <RetouchingBrush.ShowBrushes value="false" />
                  <RetouchingBrush.Type value="Details" />
                  <RetouchingBrush.Width value="10" />
                  <SaveImage.BitsPerColor value="8" />
                  <SaveImage.CompressionQuality value="1.00" />
                  <SaveImage.FileType value="tif" />
                  <SaveImage.RescaleImageToAvoidOverflow value="false" />
                  <SkewSequence.FirstImage.MaximumShiftXPct value="-3.0" />
                  <SkewSequence.FirstImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.LastImage.MaximumShiftXPct value="3.0" />
                  <SkewSequence.LastImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.NumberOfOutputImages value="3" />
                  <SkewSequence.Selected value="false" />
                  <StackingControl.FrameSkipFactor value="1" />
                  <StackingControl.FrameSkipSelected value="false" />
                  <StereoOrdering.LeftRightIndexSeparation value="1" />
                  <WatchDirectoryOptions.AcceptViaDelay value="false" />
                  <WatchDirectoryOptions.AcceptViaDelaySeconds value="2.0" />
                </Preferences>
                <TaskIndicatorCode value="2" />
              </Task>
            </Tasks>
          </Batch>
    """


    else:
        batchxml_object = """
          <Batch>
            <Sources length="1">
              <Source value="{0}" />
            </Sources>
            <ProjectDispositionCode value="101" />
            <Tasks length="1">
              <Task>
                <OutputImageDispositionCode value="2" />
                <OutputImagesDesignatedFolder value="{1}/focused/" />
                <Preferences>
                  <AcquisitionSequencer.BacklashMillimeters value="0.22" />
                  <AcquisitionSequencer.CommandLogging value="false" />
                  <AcquisitionSequencer.DistancePerStepperRotation value="1.5875" />
                  <AcquisitionSequencer.MaximumMmPerSecond value="2.0" />
                  <AcquisitionSequencer.MicrostepsPerRotation value="3200" />
                  <AcquisitionSequencer.MovementRampTime value="2.0" />
                  <AcquisitionSequencer.NumberOfSteps value="5" />
                  <AcquisitionSequencer.PrecisionThreshold value="0.05" />
                  <AcquisitionSequencer.PrerunMillimeters value="0.0" />
                  <AcquisitionSequencer.RPPIndicatorLeft value="-100.0" />
                  <AcquisitionSequencer.RPPIndicatorRight value="+100.0" />
                  <AcquisitionSequencer.SettlingTime value="3.0" />
                  <AcquisitionSequencer.ShutterActivationsPerStep value="1" />
                  <AcquisitionSequencer.ShutterAfterTime value="2.0" />
                  <AcquisitionSequencer.ShutterBetweenTime value="1.0" />
                  <AcquisitionSequencer.ShutterPulseTime value="0.3" />
                  <AcquisitionSequencer.StepSize value="0.1" />
                  <AcquisitionSequencer.StepSizeAdjustmentFactor value="1.0" />
                  <AcquisitionSequencer.StepSizesFile value="" />
                  <AlignmentControl.AddNewFilesAsAlreadyAligned value="false" />
                  <AlignmentControl.AlignmentSettingsChanged value="false" />
                  <AlignmentControl.AllowRotation value="false" />
                  <AlignmentControl.AllowScale value="false" />
                  <AlignmentControl.AllowShiftX value="false" />
                  <AlignmentControl.AllowShiftY value="false" />
                  <AlignmentControl.BrightnessSettingsChanged value="false" />
                  <AlignmentControl.CorrectBrightness value="false" />
                  <AlignmentControl.MaxRelDegRotation value="20" />
                  <AlignmentControl.MaxRelPctScale value="20" />
                  <AlignmentControl.MaxRelPctShiftX value="20" />
                  <AlignmentControl.MaxRelPctShiftY value="20" />
                  <AlignmentControl.Order.Automatic value="true" />
                  <AlignmentControl.Order.NarrowFirst value="true" />
                  <AllowReporting.UsageStatistics value="false" />
                  <ColorManagement.DebugPrintProfile value="false" />
                  <ColorManagement.InputOption value="Use_EXIF_and_DCF_rules" />
                  <ColorManagement.InputOption.AssumedProfile value="sRGB IEC61966-2.1" />
                  <ColorManagement.ManageZSDisplays value="false" />
                  <ColorManagement.ManageZSDisplaysHasChanged value="false" />
                  <ColorManagement.OutputOption value="CopyInput" />
                  <DepthMapControl.AlgorithmIdentifier value="1" />
                  <DepthMapControl.ContrastThresholdLevel value="0" />
                  <DepthMapControl.ContrastThresholdPercentile value="25.0" />
                  <DepthMapControl.EstimationRadius value="10" />
                  <DepthMapControl.SaveDepthMapImage value="false" />
                  <DepthMapControl.SaveDepthMapImageDirectory value="" />
                  <DepthMapControl.SaveUsedPixelImages value="false" />
                  <DepthMapControl.SmoothingRadius value="5" />
                  <DepthMapControl.UseFixedContrastThresholdLevel value="false" />
                  <DepthMapControl.UseFixedContrastThresholdPercentile value="true" />
                  <DepthMapControl.UsedPixelFractionThreshold value="0.5" />
                  <FileIO.UseExternalTIFFReader value="false" />
                  <Interpolator.RenderingSelection value="Interpolator.Spline4x4" />
                  <Interpolator.ShowAdvanced value="false" />
                  <LightroomPlugin.CurrentInstallationFolder value="" />
                  <LightroomPlugin.DefaultColorSpace value="AdobeRGB" />
                  <OutputImageNaming.Template value="ZS" />
                  <Precrop.LimitsString value="" />
                  <Precrop.Selected value="false" />
                  <Prerotation.Degrees value="0" />
                  <Prerotation.Selected value="false" />
                  <Presize.UserSetting.Scale value="1.0" />
                  <Presize.UserSetting.Selected value="false" />
                  <Presize.Working.Scale value="1.0" />
                  <PyramidControl.GritSuppressionMethod value="1" />
                  <PyramidControl.RetainUDRImage value="false" />
                  <RetouchingBrush.Hardness value="0.5" />
                  <RetouchingBrush.ShowBrushes value="false" />
                  <RetouchingBrush.Type value="Details" />
                  <RetouchingBrush.Width value="10" />
                  <SaveImage.BitsPerColor value="8" />
                  <SaveImage.CompressionQuality value="1.00" />
                  <SaveImage.FileType value="tif" />
                  <SaveImage.RescaleImageToAvoidOverflow value="false" />
                  <SkewSequence.FirstImage.MaximumShiftXPct value="-3.0" />
                  <SkewSequence.FirstImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.LastImage.MaximumShiftXPct value="3.0" />
                  <SkewSequence.LastImage.MaximumShiftYPct value="0.0" />
                  <SkewSequence.NumberOfOutputImages value="3" />
                  <SkewSequence.Selected value="false" />
                  <StackingControl.FrameSkipFactor value="1" />
                  <StackingControl.FrameSkipSelected value="false" />
                  <StereoOrdering.LeftRightIndexSeparation value="1" />
                  <WatchDirectoryOptions.AcceptViaDelay value="false" />
                  <WatchDirectoryOptions.AcceptViaDelaySeconds value="2.0" />
                </Preferences>
                <TaskIndicatorCode value="2" />
              </Task>
            </Tasks>
          </Batch>
    """

    return batchxml_object

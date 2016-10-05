function run2dmorph(controlFile)
% Wrapper for running batch2dmorph using settings from control file, as
% obtained via parseSettings.m.

% Obtain parameter settings
settings = parseSettings(controlFile);

% Run batch2dmorph
fprintf('Initializing run2dmorph...\n\n')
batch2dmorph(settings.directory,settings.output_dir,settings.image_extension,settings.sampleID,settings.microns_per_pixel_X,settings.microns_per_pixel_Y,settings.get_coordinates,settings.save_intermediates,settings.intensity_range_in,settings.intensity_range_out,settings.gamma,settings.threshold_adjustment,settings.smoothing_sigma,settings.noise_limit,settings.downsample,settings.num_points,settings.draw_ar)
end
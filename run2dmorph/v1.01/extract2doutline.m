function [obj_final,obj_edge,obj_smooth,sampleID,objectID] = extract2doutline(focused_image,sampleID,save_intermediates,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,smoothing_sigma)
%Output:
%
%   FILES:
%   If save_intermediates == false (default), a single image file named
%   'sampleID_objectID_final.tif'. Otherwise, eight additional images
%   showcasing the image processing steps for edge extraction will also be
%   outputted for troubleshooting purposes.
%
%   All output files are saved to a directory named 'morph2d' nested in the
%   folder containing the image file(s).
%
%   VARIABLES:
%   obj_final: a logical matrix specifying the black and white isolated
%   image of the foram in the input image. 
%
%   obj_edge: a logical matrix specifying the edge of the foram in the
%   input image.
%
%   obj_smooth: a logical matrix specifying the smoothed edge of the foram
%   in the input image.
%
%   sampleID: a string specifying the sample ID of the focused image
%   (functions as a object identifier for downstream processing).
%
%   objectID: a string specifying the object name of the focused image
%   (functions as a object identifier for downstream processing).
%
%Input Variables:
% 
%   focused_image: file name of original image. (REQUIRED)
%
%   sampleID: a string specifying the sampleID of the object. (REQUIRED)
%
%   save_intermediates: a boolean value specifying if images of intermediate
%   steps (e.g., grayscaled image, thresholded black & white image, etc.) 
%   should be saved. If save_intermediates == true, intermediate images will
%   be saved to the same folder as the focused_image with the file names
%   'focused_image_grayscale.tif', 'focused_image_bw.tif', etc. If
%   save_intermediates == false, only the final outlined image will be saved.
%   (Default value: false)
%
%   intensity_range_in, intensity_range_out, gamma: variables for intensity
%   filtering/contrast adjustment. (Default Values: [0 0.5], [0 1], 1)
%          Custom values are set with the following format:
%               intensity_range_in = [0 0.3]
%               intensity_range_out = [0 1]
%               gamma = 3
%   See:
%       http://www.mathworks.com/help/images/ref/imadjust.html
%       http://www.mathworks.com/help/images/contrast-adjustment.html  
%
%   threshold_adjustment: variable for modifying automatic threshold value
%   during conversion of image to black & white. Higher values correspond
%   with higher tolerance. The specified value will be added to the
%   automatically calculated threshold value of the grayscale image.
%   (Default value: 0)
%
%   smoothing_sigma: an integer that indicates how much smoothing should be
%   applied to the edge outline (for calculating rugosity in measuremorph.m).
%   The higher the value of smoothing_sigma, the more smoothing that will be
%   applied. (Default value: 7)
%

% Check number of arguments and set default values as necessary
narginchk(2,8);
if ~exist('save_intermediates','var') || isempty(save_intermediates), save_intermediates = false; end
if ~exist('intensity_range_in','var') || isempty(intensity_range_in), intensity_range_in = [0 0.2]; end
if ~exist('intensity_range_out','var') || isempty(intensity_range_out), intensity_range_out = [0 1]; end
if ~exist('gamma','var') || isempty(gamma), gamma = 2; end
if ~exist('threshold_adjustment','var') || isempty(threshold_adjustment), threshold_adjustment = 0; end
if ~exist('smoothing_sigma','var') || isempty(smoothing_sigma), smoothing_sigma = 7; end

% Read in original image, open the image morphologically, apply gamma
% filter
obj = imread(focused_image);
obj_open = imopen(obj,strel('disk',10));
obj_gamma = imadjust(obj_open,intensity_range_in,intensity_range_out,gamma);

% Determine most common hue and apply RGB filter
hues = [length(find(obj_gamma(:,:,1) == 255)) length(find(obj_gamma(:,:,2) == 255)) length(find(obj_gamma(:,:,3) == 255))];
[~,index] = max(hues);
if index == 1
    obj_rgbfilter = imadjust(obj_gamma,[0.2 0.3 0; 0.6 0.6 1],[]);
    obj_rgbfilter(:,:,2) = 0;
    obj_rgbfilter(:,:,3) = 0;
elseif index == 2
    obj_rgbfilter = imadjust(obj_gamma,[0.3 0.2 0; 0.6 0.6 1],[]);
    obj_rgbfilter(:,:,1) = 0;
    obj_rgbfilter(:,:,3) = 0;
elseif index == 3
    obj_rgbfilter = imadjust(obj_gamma,[0 0.3 0.2; 1 0.6 0.6],[]);
    obj_rgbfilter(:,:,1) = 0;
    obj_rgbfilter(:,:,2) = 0;
end

% Convert to grayscale and black & white
obj_gray = rgb2gray(obj_rgbfilter);
obj_bw = im2bw(obj_gray,graythresh(obj_gray) + threshold_adjustment);

% Fill holes, remove border objects, and delete remaining background noise
% from thresholded object
obj_fill = imfill(obj_bw,'holes');
obj_border = imclearborder(obj_fill);

% Remove noisy objects from image that are 5% of the total image size or
% smaller
temp_size = size(obj);
image_size = temp_size(1) * temp_size(2);
noise_limit = ceil(0.05 * image_size);
obj_final = bwareaopen(obj_border,noise_limit,4);

% Extract unsmoothed and smoothed edges
obj_edge = edge(obj_final);
obj_smooth = edge(obj_final,'canny',[],smoothing_sigma);

% Save output files
    % Make output directory if it doesn't exist
    if ~exist('morph2d','dir'), mkdir('morph2d'); end
    % Designate sampleID value
    sampleID = char(sampleID);
    % Generate objectID value
    temp = strsplit(focused_image,'.');
    objectID = strjoin(temp(1:end-1),'.');
    % Check current architecture and assign appropriate path divider
    % (solidus or reverse solidus)
    architecture = computer;
    if strcmp(computer,'MACI64') == 1 || strcmp(computer,'GLNXA64') == 1, path_divider = '/'; else path_divider = '\'; end
    % Save intermediate images for option save_intermediates == true
    if save_intermediates == true
        % Write intermediate files
        imwrite(obj_open,strcat('morph2d',path_divider,sampleID,'_',objectID,'_1_open.tif'));
        imwrite(obj_gamma,strcat('morph2d',path_divider,sampleID,'_',objectID,'_2_gamma.tif'));
        imwrite(obj_rgbfilter,strcat('morph2d',path_divider,sampleID,'_',objectID,'_3_rgbfilter.tif'));
        imwrite(obj_gray,strcat('morph2d',path_divider,sampleID,'_',objectID,'_4_grayscale.tif'));
        imwrite(obj_bw,strcat('morph2d',path_divider,sampleID,'_',objectID,'_5_bw.tif'));
        imwrite(obj_fill,strcat('morph2d',path_divider,sampleID,'_',objectID,'_6_fill.tif'));
        imwrite(obj_border,strcat('morph2d',path_divider,sampleID,'_',objectID,'_7_border.tif'));
        imwrite(obj_final,strcat('morph2d',path_divider,sampleID,'_',objectID,'_8_noise.tif'));
        imwrite(obj_edge,strcat('morph2d',path_divider,sampleID,'_',objectID,'_9_edge.tif'));
        imwrite(obj_smooth,strcat('morph2d',path_divider,sampleID,'_',objectID,'_10_smooth.tif'));
    end
    % Write final image comparing edge outline to original image
    comparison = imfuse(obj,obj_edge,'diff');
    imwrite(comparison,strcat('morph2d',path_divider,sampleID,'_',objectID,'_final.tif'));
end

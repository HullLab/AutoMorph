function [obj_final,obj_edge,obj_smooth,sampleID,objectID] = extract2doutline(focused_image,image_name,sampleID,save_intermediates,intensity_range_in,intensity_range_out,gamma,threshold_adjustment,smoothing_sigma,noise_limit)
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
%Output Variables:
%
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
%   filtering/contrast adjustment. (Default Values: [0 0.2], [0 1], 2)
%  		See:
%       	http://www.mathworks.com/help/images/ref/imadjust.html
%       	http://www.mathworks.com/help/images/contrast-adjustment.html  
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
%	limit: a float that specifies the proportion of total image size below which
%	objects should be removed during the noise-deletion stage. For instance, if
%	limit = 0.05, then all objects whose size are smaller or equal to 5% of the
%	total image size will be deleted. (Default value: 0.05)
%

% Check number of arguments and set default values as necessary
narginchk(2,10);
if ~exist('save_intermediates','var') || isempty(save_intermediates), save_intermediates = false; end
if ~exist('intensity_range_in','var') || isempty(intensity_range_in), intensity_range_in = [0 0.2]; end
if ~exist('intensity_range_out','var') || isempty(intensity_range_out), intensity_range_out = [0 1]; end
if ~exist('gamma','var') || isempty(gamma), gamma = 2; end
if ~exist('threshold_adjustment','var') || isempty(threshold_adjustment), threshold_adjustment = 0; end
if ~exist('smoothing_sigma','var') || isempty(smoothing_sigma), smoothing_sigma = 7; end
if ~exist('noise_limit','var') || isempty(noise_limit), noise_limit = 0.05; end

% Read in original image, open the image morphologically, apply gamma
% filter
obj = focused_image;
obj_open = imopen(obj,strel('disk',10));
obj_gamma = imadjust(obj_open,intensity_range_in,intensity_range_out,gamma);

% Determine most common hue and apply RGB filter
R = obj_gamma(:,:,1);
G = obj_gamma(:,:,2);
B = obj_gamma(:,:,3);
hues = [sum(R(:)) sum(G(:)) sum(B(:))];
[~,index] = max(hues);
if index == 1
    obj_gamma(:,:,2) = 0;
    obj_gamma(:,:,3) = 0;
    obj_rgbfilter = imadjust(obj_gamma,[0.1 0 0; 0.5 1 1],[]);
elseif index == 2
    obj_gamma(:,:,1) = 0;
    obj_gamma(:,:,3) = 0;
    obj_rgbfilter = imadjust(obj_gamma,[0 0.1 0; 1 0.5 1],[]);
elseif index == 3
    obj_gamma(:,:,1) = 0;
    obj_gamma(:,:,2) = 0;
    obj_rgbfilter = imadjust(obj_gamma,[0 0 0.1; 1 1 0.5],[]);
end

% Convert to grayscale and black & white
obj_gray = rgb2gray(obj_rgbfilter);
if graythresh(obj_gray) + threshold_adjustment >= 0
    obj_bw = im2bw(obj_gray,graythresh(obj_gray) + threshold_adjustment);
else
    obj_bw = im2bw(obj_gray,graythresh(obj_gray));
    fprintf('Threshold adjustment value too large! Using automatic value for %s.\n',image_name);
end

% Fill holes, remove border objects, and delete remaining background noise
% from thresholded object
%obj_fill = imfill(obj_bw,'holes');
obj_border = imclearborder(obj_bw);

% Remove noisy objects from image that are 5% of the total image size or
% smaller
temp_size = size(obj);
image_size = temp_size(1) * temp_size(2);
noise_limit_size = ceil(noise_limit * image_size);
obj_final = bwareaopen(obj_border,noise_limit_size,4);

% Extract unsmoothed and smoothed edges
    % Get unsmoothed edge
    obj_edge = edge(obj_final);
    % Get smoothed edge and delete small (relative to entire perimeter)
    % unconnected components that may result during smoothing process...
    if ~max(obj_final(:)) == 0
        obj_smooth_temp = edge(obj_final,'canny',[],smoothing_sigma);
        smooth_perimeter = regionprops(obj_smooth_temp,'Perimeter');
        perim_limit = ceil(smooth_perimeter(1).Perimeter * 0.05);
        obj_smooth = bwareaopen(obj_smooth_temp,perim_limit);
    % ...unless object is empty
    else
        obj_smooth = edge(obj_final,'canny',[],smoothing_sigma);
    end
    
% Save output files
    % Make output directory if it doesn't exist
    if ~exist('morph2d','dir'), mkdir('morph2d'); end
    % Designate sampleID value
    sampleID = char(sampleID);
    % Generate objectID value
    temp = strsplit(image_name,'.');
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

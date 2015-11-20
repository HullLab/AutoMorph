function moveSkipped(morph3d_path,skipped,image_name)
% Moves folders for skipped objects (i.e., 2D outline extraction fails)
% from 'stackfocused' folder into 'skipped' folder (both nested within the
% 'morph3d' folder).

skipped_path = fullfile(morph3d_path,'skipped');
if skipped == true
    if ~exist(skipped_path,'dir'), mkdir(skipped_path); end
    src_path = fullfile(morph3d_path,'stackfocused',image_name);
    dst_path = fullfile(skipped_path,image_name);
    copyfile(src_path,dst_path);
end
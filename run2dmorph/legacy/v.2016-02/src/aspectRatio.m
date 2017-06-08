function [H,W,aspect_ratio] = aspectRatio(output_dir,sampleID,objectID,final_table_smoothed)

set(0,'DefaultFigureVisible','off');

% Get coordinates for calculating minimum bounding box
points = [final_table_smoothed.x_smoothed final_table_smoothed.y_smoothed];

% Get minimum bounding box and coordinates
bb = minBoundingBox(points');
x = bb(1,:);
y = bb(2,:);

% Get width and height of minimum bounding box
distances = pdist(bb','euclidean');
W = min(distances);
H = median(distances);

% Calculate aspect ratio
aspect_ratio = H/W;

% Generate figure
    % Plot object outline
    figure,scatter(final_table_smoothed.x_smoothed,final_table_smoothed.y_smoothed,'.');
    axis equal;
    hold on;
    % Plot minimum bounding box
    plot(bb(1,[1:end 1]),bb(2,[1:end 1]),'r');
    % Write aspect ratio label
    AR_label = strcat('Aspect Ratio=',num2str(aspect_ratio,'%.4f'));
    y_lim = get(gca,'YLim');
    x_lim = get(gca,'XLim');
    text(x_lim(2),y_lim(2),AR_label,'VerticalAlignment','top','HorizontalAlignment','right')
    hold off;

% Save output files
    % Save image file
    saveas(gcf,fullfile(output_dir,strcat(sampleID,'_',objectID,'_aspectratio.tif')),'tiff');
end







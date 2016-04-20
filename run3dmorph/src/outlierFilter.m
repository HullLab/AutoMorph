function center_value = check_outlier3(matrix)
    % Get center index value (dependent on size of neighborhood matrix)
    size_matrix = size(matrix);
    center_index = ceil(size_matrix(1)^2 / 2);
    % Calculate quartiles of all values in neighborhood
    new_array = reshape(matrix,1,numel(matrix));
    quartiles = quantile(new_array,[0.25,0.5,0.75]);
    mean = quartiles(2);
    median_value = median(new_array);
    q25 = quartiles(1);
    q75 = quartiles(3);
    % Replace middle element of neighborhood with mean if outside inner
    % quartile range
    if matrix(center_index) < q25 || matrix(center_index) > q75
        matrix(center_index) = median_value;
    % Maintain non-outliers
    else
        center_value = matrix(center_index);
    end
    center_value = matrix(center_index);
end
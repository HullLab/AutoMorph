function index = closest(image, list, X, Y)

distance = zeros(size(list, 1), 1);

Y = Y * size(image,1);
X = X * size(image,2);

%fprintf('Picking closest to: %d %d \n', int64(Y), int64(X));


for n = 1:size(list,1)
  objectY = list(n).BoundingBox(2) + (0.5 * list(n).BoundingBox(4));
  objectX = list(n).BoundingBox(1) + (0.5 * list(n).BoundingBox(3));

	distance(n) = sqrt((X-objectX)^2 + (Y-objectY)^2);

	%fprintf('Distance to %d x %d is : %d \n', int64(objectX), int64(objectY), int64(distance(n)));
end

[ minimum, index ] = min(distance);


%objectX = list(index).BoundingBox(1) + (0.5 * list(index).BoundingBox(3));
%objectY = list(index).BoundingBox(2) + (0.5 * list(index).BoundingBox(4));
%fprintf('MIN: %f, %d ( %d x %d ) [ %f x %f ] \n', minimum, index, objectX, objectY, (objectX / size(image,1)), (objectY / size(image,2)));

end


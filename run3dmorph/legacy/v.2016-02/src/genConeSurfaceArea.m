function coneSurfaceArea = genConeSurfaceArea(centroid,height,outlineCoordinates)
% Original version by Andrew Wells (C3O Consulting; 12-08-15)
% Updated for AutoMorph by Allison Hsiang (12-10-15)
%
% Approximates the curve surface area of a generalised conical surface,
% where all points on a basal perimeter (r,phi,0) are joined by a linear
% segment to the vertex at (0,0,H) in cylindircal co-ordinates (r,phi,z)
% r>0; 0<=phi<=2*pi, H fixed constant.
%
% Note that this forumulation assumes that the first point has phi(1)
% closest to zero, and last point phi(end) is close to 2*pi, with phi
% increasing monotonically in between.
%
% The integration rule used is a midpoint rule (equivalent to approximating
% the integral via small trapeziums, but with possibly unequal width).

%x_coords = outlineCoordinates{:,1};
%y_coords = outlineCoordinates{:,2};
x_coords = outlineCoordinates.x;
y_coords = -outlineCoordinates.y;
total_coords = length(x_coords);
% Take this out if already in right format...
centroid = centroid.Centroid;

% Center coordinates on (0,0) for proper atan2 input
x_centered = x_coords - centroid(1);
y_centered = y_coords - centroid(2);
coords = [x_centered,y_centered];

% Calculate angle of inclination between coord and centroid
phis = atan2(x_centered,y_centered);
% Initialize arrays for distances
distances = zeros(1,total_coords);

% Loop through coordinates and 1) calculate distance between coord and
% centroid; and 2) add 2*pi to negative phi values to put phis on 0 to 2*pi
% scale

for i = 1:total_coords
    % (1)
    coord = coords(i,:);
    temp = [coord;centroid];
    temp_d = pdist(temp,'euclidean');
    distances(i) = temp_d;
    % (2)
    if phis(i) < 0
        phis(i) = phis(i) + 2*pi;
    end
end

H = height;
[phi,I] = sort(phis);
% Reshape hi
phi = reshape(phi,1,total_coords);
r = distances(I);

% a few consistency checks
% check r>=0
minr=min(r); % minimum r value
if(minr<0)
    % if the minimum r is negative; exit
    error('Error in input, r must be non-negative');
end

% check H>=0
if(H<0)
    % if the minimum H is negative; exit
    error('Error in input, H must be non-negative');
end

%check phi is in range 0<=phi<=2*pi
minphi=min(phi);
maxphi=max(phi);
if(minphi<0)
    % if the minimum H is negative; exit
    error('Error in input, phi must be non-negative');
end

if(maxphi>(2*pi))
    % if the max phi is greater than 2pi; exit
    error('Error in input, phi cannot be greater than 2*pi');
end

% check if phi is increasing
monphi=min(diff(phi)); % calculate differences between each successive pair of phi values, and look for the minimum value
if(monphi<0)
    % if the minimum is negative; exit
    error('Error in input, phi must be monotonically increasing');
end
% end of consistency checks

% calculate integrand at each point
y=0.5*( r.*(r.^2 + H^2.*ones(size(r)) ).^(1/2)  ); % vector of values y = 1/2*r*(r^2+H^2)^(1/2)
SA=NaN*y; % preallocate vector of right length (we will replace values below, but initially give NaN values to catch index errors)

% calculate area of trapezia between points, one by one

% first point is more complicated: area of trapezium is 
% (average of y at edges) * (change in phi), but need to subtract off 2*pi to account for phi jumping
% from 2pi back to zero as we loop around
SA(1)=0.5*(y(1)+y(end))*(phi(1)-(phi(end)-2*pi));

% for subsequent points, area of trapezium is 
% (average of y at edges) * (change in phi)
SA(2:end)=0.5*(y(1:(end-1))+y(2:end)).*(phi(2:end)-phi(1:(end-1)));

% finally output total area by summing the trapezia
coneSurfaceArea = sum(SA);

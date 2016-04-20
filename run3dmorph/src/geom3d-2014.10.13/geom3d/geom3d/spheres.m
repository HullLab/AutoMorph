function spheres(varargin)
%SPHERES Description of functions operating on 3D spheres
%
%   Spheres are represented by their center and their radius:
%   S = [xc yc zc r];
%
%   An ellipsoid is defined by:
%   ELL = [XC YC ZC A B C PHI THETA PSI]
%   where [XC YC ZY] is the center, [A B C] are length of semi-axes (in
%   decreasing order), and [PHI THETA PSI] are euler angles representing
%   the ellipsoid orientation.
%
%   See also
%   createSphere, inertiaEllipsoid
%   intersectLineSphere, intersectPlaneSphere, sphericalVoronoiDomain
%   drawSphere, drawEllipsoid
%   drawSphericalEdge, drawSphericalTriangle, drawSphericalPolygon
%   fillSphericalTriangle, fillSphericalPolygon
%
% ------
% Author: David Legland
% e-mail: david.legland@grignon.inra.fr
% Created: 2008-10-13,    using Matlab 7.4.0.287 (R2007a)
% Copyright 2008 INRA - BIA PV Nantes - MIAJ Jouy-en-Josas.

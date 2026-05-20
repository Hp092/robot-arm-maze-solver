% Create sample waypoint data for trajectory generation
% NOTE: Modify this script with your own rigid body tree and 
%       trajectory reference points
%       (We recommend saving a copy of this file)
%
% Copyright 2019 The MathWorks, Inc.

%% Common parameters

% Rigid Body Tree information
pro600 = importrobot("pro600.urdf");

%load pro600positions
eeName = 'link6';

numJoints = numel(pro600.homeConfiguration);
ikInitGuess = pro600.homeConfiguration;

% Maximum number of waypoints (for Simulink)
maxWaypoints = 20;

% Positions (X Y Z)
waypoints = [0.2883	0.1111	.0316 ; 0.382	0.2027	.0316 ; 0.2883	0.1111	.0316]'; % 3x3
         
% Euler Angles (Z Y X) relative to the home orientation       
orientations = [0     -pi/2    pi;
                0     -pi/2    pi;
                0     -pi/2    pi]';   % 3x3
            
% Array of waypoint times
waypointTimes = 0:2:4; % 1x3

% Trajectory sample time
ts = 0.2;
trajTimes = 0:ts:waypointTimes(end);
%% Additional parameters

% Boundary conditions (for polynomial trajectories)
% Velocity (cubic and quintic)
waypointVels = 0.1 *[ 0  1  0;
                     -1  -1  0;
                      1  1  0;]';

% Acceleration (quintic only)
waypointAccels = zeros(size(waypointVels));

% Acceleration times (trapezoidal only)
waypointAccelTimes = diff(waypointTimes)/4;

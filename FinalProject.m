robotArm = importrobot("URDF/pro600.urdf");
robotArm.DataFormat = 'column';
homeConfig = [8.63 -130.20 -128.53 -11.27 90.00 1.38]'*pi/180;
endEffector = 'link6';
homeTransform = getTransform(robotArm, homeConfig, endEffector);
homeTransform(1:4,4) =  [0;0;0;1];

show(robotArm,homeConfig);
axis auto;
view([230,10]); 


toolHomePos = [0.4550 0.0010 0.4340];

[rowData, colData] = csvimport('waypoints.csv', 'columns', {'Row', 'Column'});

[mappedX, mappedY] = mapper(colData, rowData);

mappedZ = 0.0692 * ones(size(mappedX));

trajectoryPoints = double([mappedX mappedY mappedZ]');

orientMatrix = ([0 -pi/2 pi]' .* ones(size(trajectoryPoints)));

% Timing and velocity initialization
trajectoryTimes = 0:2:(2 * (numel(mappedX)-1));
timeStep = 0.25;
fullTimes = 0:timeStep:trajectoryTimes(end);

velocityProfile = 0.1 * [0  1  0;
                        -1  0  0;
                         0 -1  0;
                         1  0  0;
                         0  1  0]';

accelerationProfile = zeros(size(velocityProfile));
accelerationTimes = diff(trajectoryTimes)/4;

ikSolver = inverseKinematics('RigidBodyTree',robotArm);
ikSolverWeights = [1 1 1 1 1 1];
ikInitConfig = homeConfig';
ikInitConfig(ikInitConfig > pi) = ikInitConfig(ikInitConfig > pi) - 2*pi;
ikInitConfig(ikInitConfig < -pi) = ikInitConfig(ikInitConfig < -pi) + 2*pi;

plotOption = 1;
show(robotArm,homeConfig,'Frames','off','PreservePlot',false);
hold on
if plotOption == 1
    trajectoryPlot = plot3(trajectoryPoints(1,1),trajectoryPoints(2,1),trajectoryPoints(3,1),'b.-');
end
plot3(trajectoryPoints(1,:),trajectoryPoints(2,:),trajectoryPoints(3,:),'ro','LineWidth',2);
axis auto;
view([230,10]);

applyOrientation = true; 
totalWaypoints = size(trajectoryPoints,2);
numRobotJoints = numel(robotArm.homeConfiguration);
jointConfigs = zeros(numRobotJoints,totalWaypoints);
for idx = 1:totalWaypoints
    if applyOrientation
        targetPose = trvec2tform(trajectoryPoints(:,idx)') * eul2tform(orientMatrix(:,idx)');
    else
        targetPose = trvec2tform(trajectoryPoints(:,idx)') * eul2tform([pi/2 0 pi/2]); %#ok<UNRCH> 
    end
    [configResult,~] = ikSolver(endEffector,targetPose,ikSolverWeights',ikInitConfig');
    jointConfigs(:,idx) = configResult';
end

trajectoryType = 'trap';
switch trajectoryType
    case 'trap'
        [jointPos,jointVel,jointAccel] = trapveltraj(jointConfigs,numel(fullTimes), ...
            'AccelTime',repmat(accelerationTimes,[numRobotJoints 1]), ... 
            'EndTime',repmat(diff(trajectoryTimes),[numRobotJoints 1]));
                            
    case 'cubic'
        [jointPos,jointVel,jointAccel] = cubicpolytraj(jointConfigs,trajectoryTimes,fullTimes, ... 
            'VelocityBoundaryCondition',zeros(numRobotJoints,totalWaypoints));
        
    case 'quintic'
        [jointPos,jointVel,jointAccel] = quinticpolytraj(jointConfigs,trajectoryTimes,fullTimes, ... 
            'VelocityBoundaryCondition',zeros(numRobotJoints,totalWaypoints), ...
            'AccelerationBoundaryCondition',zeros(numRobotJoints,totalWaypoints));
        
    case 'bspline'
        ctrlPoints = jointConfigs;
        [jointPos,jointVel,jointAccel] = bsplinepolytraj(ctrlPoints,trajectoryTimes([1 end]),fullTimes);
        jointVel(:,1) = zeros (7,1);    
    otherwise
        error('Invalid trajectory type! Use ''trap'', ''cubic'', ''quintic'', or ''bspline''');
end

for idx = 1:numel(fullTimes)  
 
    currentConfig = jointPos(:,idx)';
    
    eeTransform = getTransform(robotArm,currentConfig',endEffector);
    if plotOption == 1
        eePosition = tform2trvec(eeTransform);
        set(trajectoryPlot,'xdata',[trajectoryPlot.XData eePosition(1)], ...
                           'ydata',[trajectoryPlot.YData eePosition(2)], ...
                           'zdata',[trajectoryPlot.ZData eePosition(3)]);
    elseif plotOption == 2
        plotTransforms(tform2trvec(eeTransform),tform2quat(eeTransform),'FrameSize',0.05);
    end
 
    show(robotArm,currentConfig','Frames','off','PreservePlot',false);
    title(['Trajectory at t = ' num2str(fullTimes(idx))])
    drawnow   
    
end

ikSolver = inverseKinematics('RigidBodyTree', robotArm);
ikSolverWeights = [1 1 1 1 1 1];
ikInitConfig = homeConfig';

numTrajectoryPoints = size(trajectoryPoints, 2);
jointAnglesMatrix = zeros(numRobotJoints, numTrajectoryPoints);

for idx = 1:numTrajectoryPoints
    computedPose = trvec2tform(trajectoryPoints(:, idx)') * eul2tform(orientMatrix(:, idx)');
    [jointConfig, ~] = ikSolver(endEffector, computedPose, ikSolverWeights, ikInitConfig');
    jointAnglesMatrix(:, idx) = jointConfig';
end

jointAnglesMatrix = jointAnglesMatrix*180/pi;

disp('Joint angles for each waypoint:');

csvPath = 'ik_joint_angles.csv';
csvHeaders = {'Joint1', 'Joint2', 'Joint3', 'Joint4', 'Joint5', 'Joint6'};
jointAnglesWithHeaders = [csvHeaders; num2cell(jointAnglesMatrix')];
writecell(jointAnglesWithHeaders, csvPath);
disp(['Joint angles saved to ' csvPath]);

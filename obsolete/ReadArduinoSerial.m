clear('classes') %#ok<CLCLS>
delete(instrfindall)
s1 = serial('com3');
fopen(s1);
s1.ReadAsyncMode = 'continuous';
readasync(s1);

h = axes;
data = [];

flushinput(s1);
while ishandle(h)
    if  s1.BytesAvailable
        try
            data = [data; str2num(s1.fscanf)];
        catch
            data =  [data; [NaN, NaN, NaN]];
            warning('sensor data capturing failed')
        end
        flushinput(s1);
        plot(data(:,2))
        drawnow
    end
end

% tic
% str2num(s1.fscanf)
% toc
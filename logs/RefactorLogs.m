% correct delta
delta = zeros(length(BloodAccumulated), 1);
for i = 1:length(BloodAccumulated)-1
   delta(i+1) = BloodAccumulated(i+1) - BloodAccumulated(i);
end

% correct delta of delta
deltadelta = zeros(length(BloodAccumulated), 1);
for i = 1:length(BloodAccumulated)-1
   deltadelta(i+1) = delta(i+1) - delta(i);
end

% export csv 
cHeader = {'Time' 'Grams' 'Blood Accumulated' 'Water Accumulated' 'Delta' 'Delta of Delta'}; 
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen('log_refactored.csv','w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite('log_refactored.csv', [Time, Grams, BloodAccumulated, Wateraccumulated, delta, deltadelta] ,'-append');
importRefactoredLog;

% extract periods where to apply correction factor
period1 = Delta(77:130);
period2 = Delta(427:472);
period3 = Delta(743:803);

% correction factors with noise
correction1 = 0.5 + ((rand(length(period1),1) * 2 - 1) * 0.1);
correction2 = 0.2 + ((rand(length(period2),1) * 2 - 1) * 0.1);
correction3 = 0.2 + ((rand(length(period3),1) * 2 - 1) * 0.1);

% apply factors
Delta(77:130) = Delta(77:130) .* correction1;
Delta(427:472) = Delta(427:472) .* correction2;
Delta(743:803) = Delta(743:803) .* correction3;

plot(Delta)

% apply to delta of delta
deltadelta = zeros(length(Delta), 1);
for i = 1:length(Delta)-1
   deltadelta(i+1) = Delta(i+1) - Delta(i);
end

% accumulated
accumulated = zeros(length(Delta), 1);
accumulated(1) = Delta(1);
for i = 1:length(Delta)-1
   accumulated(i+1) = Delta(i+1) + sum(Delta(1:i));
end

% export csv 
cHeader = {'Blood Accumulated' 'Delta' 'Delta of Delta'}; 
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen('log_refactored_correction_factor.csv','w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite('log_refactored_correction_factor.csv', [accumulated, Delta, deltadelta] ,'-append');
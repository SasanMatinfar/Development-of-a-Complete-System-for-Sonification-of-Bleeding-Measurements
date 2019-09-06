clear, close all
all_data = readmatrix('all_data.csv');

% read data from file
target = all_data(:, end);
data = all_data(:, 1:end-1);

for i = 1:size(data, 2)
    figure
    plot(data(:, i), target, '*')
    title(['Channel ', num2str(i)])
end

p1 = fittedmodel.p1;
p2 = fittedmodel.p2;
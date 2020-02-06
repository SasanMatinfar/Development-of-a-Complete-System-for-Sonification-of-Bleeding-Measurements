function result = plot_square(volume, vol_max)

    x1=-3.5;
    x2=-2.75;
    y1=0;
    y2=volume*2/vol_max;
    x = [x1, x2, x2, x1, x1];
    y = [y1, y1, y2, y2, y1];
    fill(x, y, 'red');
    hold on;
    xlim([-5, 3]);
    ylim([-1, 3]);

result = 1;
end
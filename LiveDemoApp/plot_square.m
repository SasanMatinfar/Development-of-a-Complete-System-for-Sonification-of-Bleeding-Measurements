function result = plot_square()

    x1=-3.5;
    x2=-2.75;
    y1=0;
    y2=2;
    x = [x1, x2, x2, x1, x1];
    y = [y1, y1, y2, y2, y1];
    plot(x, y, 'k-', 'LineWidth', 0.5);
    hold on;
    xlim([-5, 3]);
    ylim([-1, 3]);

result = 1;
end
function result = plot_anim(start, stop, volume, vol_max)
    set(gcf, 'Position',  [100, 100, 1000, 400])
    h(1) = subplot(1, 2, 1);
    set(h(1), 'position', [100, 100, 200, 400]);
    x1=0;
    x2=0.75;
    y1=0;
    y2=volume*2/vol_max;
    x = [x1, x2, x2, x1, x1];
    y = [y1, y1, y2, y2, y1];
    fill(x, y, 'red');
    hold on;
    xlim([-2, 3]);
    ylim([-1, 3]);

    y3=2;
    x = [x1, x2, x2, x1, x1];
    y = [y1, y1, y3, y3, y1];
    plot(x, y, 'k-', 'LineWidth', 0.5);
    hold on;
    xlim([-2, 3]);
    ylim([-1, 3]);

    subplot(1, 2, 2)
    for i = linspace(start, stop, 20)
       cla
       plot(0.5, 1, '.r', 'MarkerSize',i)
       drawnow
       pause(0.05)
    end

result = 1;
end
function result = plot_anim(start,stop)

    for i = linspace(start, stop, 20)
       plot(1, 1, '.r', 'MarkerSize',i)
       drawnow
       pause(0.05)
    end

result = 1;
end


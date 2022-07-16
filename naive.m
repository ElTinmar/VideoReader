function naive(videofile)

    function process(frame, frame_num)
        frame_double = im2double(frame);
        [U,S,V] = svd(frame_double);
        disp(frame_num)

    end

    mov = VideoReader(videofile);

    frame_num = 0;
    while mov.hasFrame
        frame = mov.readFrame();
        
        frame_gray = frame(:,:,1);
        frame_num = frame_num +1 ;
        process(frame_gray, frame_num)
    end
end

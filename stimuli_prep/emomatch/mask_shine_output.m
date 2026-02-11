% Checkerboards
% read images
imformat = 'png';
input_folder_cb = fullfile('SHINE_OUTPUT', 'soco_emomatch_cb');
output_folder = fullfile('SHINE_MASKED', 'cb');
[images_cb,numim_cb,imname_cb] = readImages(input_folder_cb,imformat);
numim_cb = max(size(images_cb));

average_cb = avgHist(images_cb);

% apply mask
mask_cb = imread('/manual/mask/cb_mask.png');

image_cb_masked = {};
for ii = 1:numim_cb
    tmp = images_cb{ii};
    masked_im = tmp;
    masked_im(mask_cb == 127) = 127;
    image_cb_masked{ii} = masked_im;
    imwrite(image_cb_masked{ii},fullfile(output_folder,strcat('SHINEd_masked_',imname_cb{ii})));
end

average_cb_mask = avgHist(image_cb_masked);
average_cb_mask_noback = average_cb_mask;
average_cb_mask_noback(128) = [];

% Check histograms
figure, plot(average_cb)
figure, plot(average_cb_mask_noback)


% faces
% read images
imformat = 'png';
input_folder_faces = fullfile('SHINE_OUTPUT', 'soco_emomatch_faces');
output_folder = fullfile('SHINE_MASKED', 'faces');
[images_faces,numim_faces,imname_faces] = readImages(input_folder_faces,imformat);
numim_faces = max(size(images_faces));

average_faces = avgHist(images_faces);

% apply mask
mask_faces = imread('/manual/mask/face_mask.png');

image_face_masked = {};
for ii = 1:numim_faces
    tmp = images_faces{ii};
    masked_im = tmp;
    masked_im(mask_faces == 127) = 127;
    image_face_masked{ii} = masked_im;
    imwrite(image_face_masked{ii},fullfile(output_folder,strcat('SHINEd_masked_',imname_faces{ii})));
end

average_face_mask = avgHist(image_face_masked);
average_face_mask_noback = average_face_mask;
average_face_mask_noback(128) = [];

% Check histograms
figure, plot(average_faces)
figure, plot(average_face_mask_noback)

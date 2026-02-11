% read images
imformat = 'png';
input_folder = fullfile('MATLAB', 'SHINEtoolbox','SHINE_OUTPUT', 'soco_emomatch_faces');

[images,numim,imname] = readImages(input_folder,imformat);
numim = max(size(images));

average = avgHist(images);

cd '/MATLAB/SHINEtoolbox/SHINE_TEMPLATE'
save template_histo average


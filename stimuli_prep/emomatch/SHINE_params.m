%% SHINE Faces
% SHINE
% SHINE options    [1=default, 2=custom]: 2
% Matching mode    [1=luminance, 2=spatial frequency, 3=both]: 3
% Matching of both [1=hist&sf, 2=hist&spec, 3=sf&hist, 4=spec&hist]: 1
% Optimize SSIM    [1=no, 2=yes]: 2
% # of iterations? 3
% Matching region  [1=whole image, 2=foreground/background]: 2
% Segmentation of: [1=source images, 2=template(s)]: 1
% Image background [1=specify lum, 2=find automatically (most frequent lum in the image)]: 2


%% Generate template histogram from SHINEd faces
% run this:
% /social_carousel/stimuli_prep/emomatch/create_template_SHINE.m


%% SHINE checkerboards
% SHINE_histo
% SHINE options    [1=default, 2=custom]: 2
% Matching mode    [1=luminance, 2=spatial frequency, 3=both]: 3
% Matching of both [1=hist&sf, 2=hist&spec, 3=sf&hist, 4=spec&hist]: 1
% Optimize SSIM    [1=no, 2=yes]: 2
% # of iterations? 3
% Matching region  [1=whole image, 2=foreground/background]: 1


%% Apply mask to make background uniform
% run this:
% /social_carousel/stimuli_prep/emomatch/mask_shine_output.m

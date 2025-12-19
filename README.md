# Welcome to the social carousel 🎠 

This repository contains all the scripts you need to run the behavioural paradigms for fMRI sequences of the SoCo study (henceforth: the carousel).

The carousel was developed and tested on `PsychoPy 2024.2.5`, and compatibility with other psychopy versions is NOT garanteed. You can download it [here](https://github.com/psychopy/psychopy/releases/tag/2024.2.5 ). From our limited testing with older `PsychoPy` versions, known issues include trouble with a/v sync which will affect the `movie` module.

## Setup 🖥️

Note: If you're running the task on the stimulus computer at the 7T scanner of the MPI CBS, you can skip the setup.

- Clone (`git clone`) or download (as `.zip`) the repo to your local machine
- The stimuli can be downloaded [here](https://owncloud.gwdg.de/index.php/s/5onMUgVcrZSakzB) - just ask Jessica for the pw.
  - If you change anything in the stimuli or instructions, please also update the change log and push to the repo.
  - Any local changes (e.g. at the scanner) should be uploaded to the owncloud
- Keep the same directory structure as in the `.zip` file you just downloaded.
- Update `config.json`.
  - "io_root_dir" contains the root path to the stimuli, logs, instructions.
  - "repo_dir" is the path to the repository cloned/downloaded in the first step.
  - After updating to your ow paths, the file shoudl look like this:
    ```
    {
      "io_root_dir": "/Path/to/social_carousel_io",
      "repo_dir": "/Path/to/social_carousel"
    }
    ```
    
## Running the carousel 🌈

- Open PsychoPy _**v2024.2.5**_ (NOTE THE VERSION NUMBER - an older 2022 version is also installed at the scanner, and should not be used to run the carousel)
- In the `PsychoPy Runner`, click the blue **+** sign (add experiment)
- Navigate directories to add `main.py` to the experiment list; select it and click open.
- Click the green play button (run the script in python) to launch the GUI.
- Fill out the GUI options:
  - <ins>Subject ID</ins>: The ID code for the current participant, for example: `001` (do not enter any prefix, only the number).
    - Note on Subject ID: make sure you enter the participant ID the SAME WAY across runs and sessions for the same subject! 
  - <ins>Session</ins>: Select `01` for first visit, `02` for second visit.
  - <ins>Language</ins>: To run the tasks in english, select `en`. To run the tasks in german, select `de`.
  - <ins>Mode</ins>: To run the full task, select `full`. For testing, debugging, showing examples to the participant, select `demo`. The use of the `demo` option will limit resting-state runs to 5 seconds, and task runs to one trial.
  - <ins>Select task</ins>: Select the task you want to run. Depending on your choice, another GUI might open (see next section).
- After clicking OK, another dialog box will open. This will prompt you to confirm that you are running the whole-brain or layer (narrow FoV) sequence at the scanner. This is because the order of these sessions is counterbalanced across participants. Note that this information is also logged in the scanning spreadsheet.

## The tasks 📋

The carousel includes 6 modules. The name of the module is provided as it is named in the carousel GUI:
- `cross`: Fixation cross for unconstrained cognition (resting-state)
- `movie`: Movies for naturalistic viewing (resting-state)
- `beliefs`: False beliefs task using short stories ([Dodell-Feder et al., 2011](https://www.sciencedirect.com/science/article/pii/S1053811910016241))
- `social`: Social cognition task using geometric shape movies (as implemented in HCP: [Barch et al., 2013](https://www.sciencedirect.com/science/article/pii/S1053811913005272?via%3Dihub))
- `emoinf`: Emotional inference task using short stories ([Jacoby et al., 2016](https://www.sciencedirect.com/science/article/pii/S1053811915010472))
- `emomatch`: *not yet supported* Emotion matching task using face, body, and shape images (as implemented in HCP: [Barch et al., 2013](https://www.sciencedirect.com/science/article/pii/S1053811913005272?via%3Dihub))

### Task-specific notes

The subsections below provide more details on the task-specific GUI choices.

#### `movie`
Two movie choices are currently implemented. All participants should complete both movie conditions:
- `cloudy`: Plays Pixar's Partly Cloudy animated film. Note that language choice here is irrelevant as the movie contains no language.  
- `lotr`: Plays Lord of the Rings - The Fellowship of the Ring scene (the council of Elrond). 

#### Localizers: `beliefs`, `social`, `emoinf`, `emomatch`
Each task leads to a GUI asking the user to select the task run. All participants should complete both runs:
- `1`: Select for run 1.  
- `2`: Select for run 2.

## Sequence parameters 🧲

🤔 to do 🤔

# Contributors 💞

- Jessica Royer, MPI CBS
- Lorenz Ahle, MPI CBS
- Sofie Valk, MPI CBS

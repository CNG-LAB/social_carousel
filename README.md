# Welcome to the social carousel 🎠 

This repository contains all the scripts you need to run the behavioural paradigms for fMRI sequences of the SoCo study (henceforth: the carousel).

The carousel was developed and tested on `PsychoPy 2024.2.5`, and compatibility with other psychopy versions is NOT garanteed. You can download this version [here](https://github.com/psychopy/psychopy/releases/tag/2024.2.5 ). Known issues with older PsychoPy versions in previous tests include trouble with a/v sync which will affect the movies module.

## The tasks 📋

The carousel includes 6 modules:
- Fixation cross for unconstrained cognition (resting-state) - module `cross`
- Movies for naturalistic viewing (resting-state) - module `movie`.
- False beliefs task using short stories - module `beliefs`.
- *not yet supported* Social cognition task using geometric shape movies 
- *not yet supported* Emotional inference task using short stories
- *not yet supported* Emotion matching task using face, body, and shape images

You can call each task from main.py - a GUI will open for you to select the desired task and run.

## Setup 🖥️

Note: If you're running the task on the stimulus computer at the 7T scanner of the MPICBS, you can skip the setup.

- Clone (`git clone`) or download (as `.zip`) the repo to your local machine
- The stimuli can be downloaded here: link. It's important that you keep the same directory structure as contained in the `.zip` file.
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

- Open PsychoPy _**v2024.2.5**_ (NOTE THE VERSION NUMBER)
- In the `PsychoPy Runner`, click the blue **+** sign (add experiment) and navigate directories to add `main.py` to the list (select it and click open).
- Click the green play button (run the script in python) to launch the GUI. Fill out the options:
  - Subject ID: The ID code for the current participant, for example: `sub-001`
  - Session: Enter `01` for first visit, `02` for second visit.
  - Language: To run the tasks in english, select `en`. To run the tasks in german, select `de`.
  - Mode: To run the full task, select `full`. For testing, debugging, showing examples to the participant, select `demo`.
  - Select task: Select the task you want to run (see section `The tasks`). Depending on your choice, another GUI might open.

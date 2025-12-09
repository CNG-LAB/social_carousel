# main.py
from psychopy import gui, core
import importlib
from utilities import getConfig
import pathlib
import os

def main():
    
    # List of fMRI tasks
    # This name will appear in the GUI
    # note: task .py script name must match with one entry in this list (cross -> cross.py)
    list_of_tasks = ["cross", "movie", "beliefs", "social", "emoinf", "emomatch"]

    # -----------------------------
    # DIRECTORIES CHECK
    # -----------------------------

    # Get directories according to config file
    path_to_config = pathlib.Path(__file__).parent.parent
    filename = os.path.join(path_to_config, "config.json")
    configDirs = getConfig(filename)
    message_repo_dir = 'NOTE: Config file says social carousel repo is here: {this_dir}'.format(this_dir=configDirs['repo_dir'])
    print(message_repo_dir)
    message_root_dir = 'NOTE: Config file says your input/output directory is here: {this_dir}'.format(this_dir=configDirs['io_root_dir'])
    print(message_root_dir)
    
    # Check if io (sub)directories exist
    try:

        if pathlib.Path(configDirs['io_root_dir']).exists():
            print('Found input/output directory')
        else:
            logsDir = os.path.join(configDirs['io_root_dir'], "logs")
            instructionsDir = os.path.join(configDirs['io_root_dir'], "instructions")
            stimDir = os.path.join(configDirs['io_root_dir'], "stimuli")
            if pathlib.Path(logsDir).exists():
                print('Found logs directory')
            if pathlib.Path(instructionsDir).exists():
                print('Found instructions directory')
            if pathlib.Path(stimDir).exists():
                print('Found stimuli directory')

    except Exception as e:
        print("Refer to README in social carousel repo for expected structure.")
        print("ERROR in directory setup: ")
        print(e)
        core.quit()

    # -----------------------------
    # GUI SETUP
    # -----------------------------
    dlg = gui.Dlg(title="Social Carousel")
    dlg.addField("Subject ID (format example: 001, 002, ... 050):")
    dlg.addField("Session:", choices=["01", "02"])
    dlg.addField("Language:", choices=["de", "en"])
    dlg.addField("Mode:", choices=["full", "demo"])
    dlg.addField("Select Task:", choices=list_of_tasks)

    user_input = dlg.show()

    if dlg.OK == False:
        core.quit()

    subject_id = user_input[0]
    session = user_input[1]
    language = user_input[2]
    demo = user_input[3]
    task_choice = user_input[4]

    # -----------------------------
    # Special extra GUI for specific tasks
    # -----------------------------
    run_number = None
    if task_choice == "beliefs" or task_choice == "social" or task_choice == "emoinf" or task_choice == "emomatch":
        dlg2 = gui.Dlg(title="localizer options")
        dlg2.addField("Select run:", choices=["1", "2"])
        run_input = dlg2.show()

        if dlg2.OK == False:
            core.quit()

        run_number = run_input[0]

    elif task_choice == "movie":
        dlg2 = gui.Dlg(title="movie options")
        dlg2.addField("Select movie:", choices=["cloudy", "lotr"])
        movie_input = dlg2.show()

        if dlg2.OK == False:
            core.quit()

        movie_id = movie_input[0]

    # -----------------------------
    # Map GUI selection: module name
    # -----------------------------
    task_map = {
        list_of_tasks[0]: list_of_tasks[0],
        list_of_tasks[1] : list_of_tasks[1],
        list_of_tasks[2] : list_of_tasks[2],
        list_of_tasks[3] : list_of_tasks[3],
        list_of_tasks[4] : list_of_tasks[4],
        list_of_tasks[5] : list_of_tasks[5]
    }

    task_module_name = task_map[task_choice]

    # -----------------------------
    # Dynamically import and run task
    # Each task script must contain a run_task() function
    # -----------------------------
    try:
        task_module = importlib.import_module(task_module_name)

        # Call correct version of the task
        if task_choice == "beliefs" or task_choice == "social" or task_choice == "emoinf" or task_choice == "emomatch":
            task_module.run_task(subject_id, session, language, demo, run_number)
        elif task_choice == "movie":
            task_module.run_task(subject_id, session, language, demo, movie_id)
        else:
            task_module.run_task(subject_id, session, language, demo)

        print("Task execution finished.")
    
    except Exception as e:
        print("ERROR while running task:")
        print(e)
        core.quit()

if __name__ == "__main__":
    main()

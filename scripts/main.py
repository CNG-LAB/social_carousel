# main.py
from psychopy import gui, core
import importlib
from utilities import getConfig, is_valid_subject_id
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

    info = {
        "Subject ID (format example: 001, 002, ... 050):": "",
        "Session:": ["01", "02"],
        "Language:": ["de", "en"],
        "Mode:": ["full", "demo"],
        "Select Task:": list_of_tasks
    }

    dlg = gui.DlgFromDict(dictionary=info, 
        title="Social Carousel", 
        tip=None, 
        sortKeys=False
    )

    if dlg.OK == False:
        core.quit()

    subject_id = info["Subject ID (format example: 001, 002, ... 050):"]
    session = info["Session:"]
    language = info["Language:"]
    demo = info["Mode:"]
    task_choice = info["Select Task:"]

    # -----------------------------
    # Check inputs
    # -----------------------------

    # is subject ID a three digit entry
    if not is_valid_subject_id(subject_id):
        print("Invalid subject ID! It must be a zero-padded 3-digit number (e.g., 001).")
        core.quit()

    # Ask user to confirm session type
    this_pair = (int(subject_id) - 1) // 2 + 1 
    startWithWholeBrain = (this_pair % 2) == 1
    if startWithWholeBrain is True and session == "01":
        this_message = "Session 01 is WHOLE BRAIN"
    elif startWithWholeBrain is True and session == "02": 
        this_message = "Session 02 is LAYER"
    elif startWithWholeBrain is False and session == "01": 
        this_message = "Session 01 is LAYER"
    elif startWithWholeBrain is False and session == "02": 
       this_message = "Session 02 is WHOLE BRAIN"
    else:
        print("Invalid subject/session combination.")
        core.quit()

    dlg_order = gui.Dlg(title="For this subject...")
    dlg_order.addText(this_message + "\nPress OK to continue.")
    dlg_order.show()

    if not dlg_order.OK:
        core.quit()

    # -----------------------------
    # Special extra GUI for specific tasks
    # -----------------------------
    run_number = None
    
    if task_choice == "beliefs" or task_choice == "social" or task_choice == "emoinf" or task_choice == "emomatch":
        infoRun = {
            "Select run:": ["1", "2"],
        }

        dlg2 = gui.DlgFromDict(dictionary=infoRun, 
            title="Social Carousel", 
            tip=None, 
            sortKeys=False
        )
        if dlg2.OK == False:
            core.quit()

        run_number = infoRun["Select run:"]

    elif task_choice == "movie":
        infoRun = {
            "Select movie:": ["1", "2"],
        }

        dlg2 = gui.DlgFromDict(dictionary=infoRun, 
            title="Social Carousel", 
            tip=None, 
            sortKeys=False
        )
        if dlg2.OK == False:
            core.quit()

        movie_id = infoRun["Select movie:"]

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

# main.py
from psychopy import gui, core
import importlib

def main():
    # -----------------------------
    # GUI SETUP
    # -----------------------------
    dlg = gui.Dlg(title="Experiment Launcher")
    dlg.addField("Subject ID:")
    dlg.addField("Session:")
    dlg.addField("Language:", choices=["en", "de"])
    dlg.addField("Mode:", choices=["demo", "full"])
    dlg.addField("Select Task:", choices=["cross", "movie", "beliefs"])

    user_input = dlg.show()

    if dlg.OK == False:
        core.quit()

    subject_id = user_input[0]
    session = user_input[1]
    language = user_input[2]
    demo = user_input[3]
    task_choice = user_input[4]

    # -----------------------------
    # Special extra GUI for beliefs
    # -----------------------------
    run_number = None
    if task_choice == "beliefs":
        dlg2 = gui.Dlg(title="beliefs options")
        dlg2.addField("Select run:", choices=["Run 1", "Run 2"])
        run_input = dlg2.show()

        if dlg2.OK == False:
            core.quit()

        run_number = run_input[0]  # "Run 1" or "Run 2"

    elif task_choice == "movie":
        dlg2 = gui.Dlg(title="movie options")
        dlg2.addField("Select movie:", choices=["cloudy", "lotr"])
        movie_input = dlg2.show()

        if dlg2.OK == False:
            core.quit()

        movie_id = movie_input[0]  # movie 1 or movie 2

    # -----------------------------
    # Map GUI selection → module name
    # -----------------------------
    task_map = {
        "cross": "cross",
        "movie": "movie",
        "beliefs": "beliefs",
    }

    task_module_name = task_map[task_choice]

    # -----------------------------
    # Dynamically import and run task
    # Each task script must contain a run_task() function
    # -----------------------------
    try:
        task_module = importlib.import_module(task_module_name)

        # Call correct version of the task
        if task_choice == "beliefs":
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

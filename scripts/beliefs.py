# beliefs.py
# Saxe false beliefs

from psychopy import visual, event, core

def run_task(subject_id, session, run_number):
    win = visual.Window([800, 600], color="grey")

    msg = visual.TextStim(
        win,
        text=f"Task 1\n{run_number}\nSubject: {subject_id}\nSession: {session}\n\nPress any key to start.",
        font="Arial"
    )
    msg.draw()
    win.flip()
    event.waitKeys()

    # Example differing behavior for run 1 vs run 2
    stim_text = "This is Run 1" if run_number == "Run 1" else "This is Run 2"

    stim = visual.TextStim(win, text=stim_text, font="Arial")
    stim.draw()
    win.flip()
    core.wait(2)

    win.close()
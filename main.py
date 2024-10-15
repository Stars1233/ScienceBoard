import sys

sys.dont_write_bytecode = True
from chimerax import ChimeraX, ChimeraXTask

if __name__ == "__main__":
    with ChimeraX(sort="daily", port=8080, gui=True, version="0.4") as chimerax:
        single_task = ChimeraXTask(config_path="task.json", manager=chimerax)
        print(single_task.test())

import sys

sys.dont_write_bytecode = True
from sci.ChimeraX import ChimeraX, ChimeraXTask
from sci import Model, Access, Overflow
from sci.ChimeraX import ChimeraXAgent

if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    agent = ChimeraXAgent(
        model=model,
        access_handler=Access.openai,
        overflow_handler=Overflow.openai_lmdeploy,
        context_window_size=3
    )

    with ChimeraX(sort="daily", port=8080, gui=True, version="0.4") as chimerax:
        single_task = ChimeraXTask(
            agent=agent,
            config_path="example.json",
            manager=chimerax
        )
        print(single_task())

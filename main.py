import sys

sys.dont_write_bytecode = True
from sci import Model, Content, Access, Overflow
from sci.ChimeraX import ChimeraX, ChimeraXTask, ChimeraXAgent

def debug_chimerax():
    with ChimeraX(sort="daily", port=8080, gui=True, version="0.4") as chimerax:
        single_task = ChimeraXTask(
            config_path="sci/ChimeraX/tasks/example.json",
            manager=chimerax
        )
        print(single_task())

def debug_agent():
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

    agent([Content(type="text", text="Who won the world series in 2020?")])
    agent([Content(type="text", text="Where was it played?")])

    from pprint import pprint
    pprint(agent.dump_history())

if __name__ == "__main__":
    debug_agent()

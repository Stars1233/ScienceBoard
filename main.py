import sys

sys.dont_write_bytecode = True
from sci import Tester, Model, Agent, Prompts
from sci.ChimeraX import ChimeraXManagerRaw

if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    agent_dict = {
        "ChimeraXRaw": Agent(
            model=model,
            overflow_style="openai_lmdeploy",
            system_inst=Prompts.SYSTEM_INST_CHIMERAX_RAW
        )
    }

    manager_dict = {
        "ChimeraXRaw": ChimeraXManagerRaw(
            sort="daily",
            port=8080,
            gui=True,
            version="0.4"
        )
    }

    Tester(
        tasks_path="~/Downloads/tasks",
        logs_path="~/Downloads/logs",
        agents=agent_dict,
        managers=manager_dict,
        debug=True
    )()

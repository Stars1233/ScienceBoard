import sys

sys.dont_write_bytecode = True
from sci import Model, Agent, Tester
from sci.ChimeraX import ChimeraXManagerRaw

if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    agent_dict = {
        "ChimeraX": Agent(
            model=model,
            overflow_style="openai_lmdeploy"
        )
    }

    manager_dict = {
        "ChimeraX": ChimeraXManagerRaw(
            sort="daily",
            port=8080,
            gui=True,
            version="0.4"
        )
    }

    Tester(
        tasks_path="~/Downloads/tasks",
        agents=agent_dict,
        managers=manager_dict,
        logs_path="~/Downloads/logs"
    )()

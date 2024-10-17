import sys

sys.dont_write_bytecode = True
from sci.ChimeraX import ChimeraXManagerRaw, ChimeraXAgent
from sci import Model, Overflow, Tester

if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    agent_dict = {
        "ChimeraX": ChimeraXAgent(
            model=model,
            overflow_handler=Overflow.openai_lmdeploy
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

    tester = Tester(
        tasks_path="tasks",
        agents=agent_dict,
        managers=manager_dict
    )

    from pprint import pprint
    pprint(tester.task_info)

import sys

sys.dont_write_bytecode = True
from sci import Presets, Tester

if __name__ == "__main__":
    # spawn_agents() only receive keyword args from Model and Agent
    agents = Presets.spawn_agents(
        model_style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
        overflow_style="openai_lmdeploy"
    )

    Tester(
        tasks_path="./tasks",
        logs_path="./logs",
        agents=agents,
        debug=True,
        ignore=False
    )()

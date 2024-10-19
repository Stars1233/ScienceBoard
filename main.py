import sys

sys.dont_write_bytecode = True
from sci import Model, Overflow, Tester
from sci.ChimeraX import ChimeraXManagerRaw, ChimeraXAgent

if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    agent_dict = {
        "ChimeraX": ChimeraXAgent(
            model=model,
            overflow_style="openai_lmdeploy"
        )
    }

    manager_dict = {
        "ChimeraX": ChimeraXManagerRaw(
            sort="daily",
            path="C:/Program Files/ChimeraX 1.8/bin/ChimeraX-console.exe",
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

    # with manager_dict["ChimeraX"] as chimerax:
    #     image = chimerax.screenshot()
    #     import base64
    #     from io import BytesIO
    #     image.save(buffered := BytesIO(), format="JPEG")
    #     image_base64 = base64.b64encode(buffered.getvalue())
    #     print(image_base64)

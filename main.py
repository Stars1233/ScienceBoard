import sys
import os

sys.dont_write_bytecode = True
from sci import OBS, Automata, Tester

gpt_4o = lambda: Automata(
    model_style="openai",
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-4o-2024-08-06",
    api_key=os.environ["OPENAI_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="openai_gpt"
)

intern_vl = lambda: Automata(
    model_style="openai",
    base_url=os.environ["OPEN_BASE_URL"],
    model_name=os.environ["INTERN_VL_NAME"],
    overflow_style="openai_lmdeploy"
)

deepseek_vl = lambda: Automata(
    model_style="openai",
    base_url=os.environ["OPEN_BASE_URL"],
    model_name=os.environ["DEEPSEEK_VL_NAME"],
    api_key=os.environ["OPEN_API_KEY"],
    overflow_style="openai_siliconflow",
    register=Automata.image_token()
)

qwen_vl = lambda: Automata(
    model_style="openai",
    base_url=os.environ["OPEN_BASE_URL"],
    model_name=os.environ["QWEN_VL_NAME"],
    api_key=os.environ["OPEN_API_KEY"],
    overflow_style="openai_siliconflow",
    context_window=3,
    hide_text=True
)


if __name__ == "__main__":
    # execute tasks one by one
    Tester.plan([
        {
            "tasks_path": "./tasks/ChimeraX_VM",
            "logs_path": "./logs/gpt_4o-chimerax-vm-screenshot",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "obs_types": {OBS.screenshot}
        },
        {
            "tasks_path": "./tasks/ChimeraX_VM",
            "logs_path": "./logs/gpt_4o-chimerax-vm-a11y_tree",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "obs_types": {OBS.a11y_tree}
        },
        {
            "tasks_path": "./tasks/ChimeraX_VM",
            "logs_path": "./logs/gpt_4o-chimerax-vm-screenshot+a11y_tree",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "obs_types": {OBS.screenshot, OBS.a11y_tree}
        }
    ])

    # alternative for Tester.plan
    Tester(
        tasks_path="./tasks/ChimeraX_VM",
        logs_path="./logs/gpt_4o-chimerax-vm-set_of_marks",
        vm_path=os.environ["VM_PATH"],
        automata=gpt_4o(),
        obs_types={OBS.set_of_marks}
    )()

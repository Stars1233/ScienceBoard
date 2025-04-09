import sys
import os

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
from sci import OBS, Automata, Tester

gpt_4o = lambda: Automata(
    model_style="openai",
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-4o-2024-08-06",
    api_key=os.environ["OPENAI_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="openai_gpt"
)

qvq = lambda: Automata(
    model_style="openai",
    base_url=os.environ["QVQ_VL_URL"],
    model_name=os.environ["QVQ_VL_NAME"],
    overflow_style="openai_gpt",
    hide_text=True
)

qwen25_vl = lambda: Automata(
    model_style="openai",
    base_url=os.environ["QWEN_VL_URL"],
    model_name=os.environ["QWEN_VL_NAME"],
    overflow_style="openai_gpt",
    hide_text=True
)

intern_vl = lambda: Automata(
    model_style="openai",
    base_url=os.environ["INTERN_VL_URL"],
    model_name=os.environ["INTERN_VL_NAME"],
    overflow_style="openai_gpt",
    hide_text=True
)

tars_dpo = lambda: Automata(
    model_style="openai",
    base_url=os.environ["TARS_DPO_URL"],
    model_name=os.environ["TARS_DPO_NAME"],
    overflow_style="openai_gpt",
    hide_text=True
)

if __name__ == "__main__":
    # execute tasks one by one
    Tester.plan([
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-screenshot",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "headless": True,
            "obs_types": {OBS.screenshot}
        },
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-a11y_tree",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "headless": True,
            "obs_types": {OBS.a11y_tree}
        },
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-screenshot+a11y_tree",
            "vm_path": os.environ["VM_PATH"],
            "automata": gpt_4o(),
            "headless": True,
            "obs_types": {OBS.screenshot, OBS.a11y_tree}
        }
    ])

    # alternative for Tester.plan
    Tester(
        tasks_path="./tasks/VM",
        logs_path="./logs/gpt_4o-vm-set_of_marks",
        vm_path=os.environ["VM_PATH"],
        automata=gpt_4o(),
        headless=True,
        obs_types={OBS.set_of_marks}
    )()

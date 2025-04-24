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

gpt_o3 = lambda: Automata(
    model_style="openai",
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="o3-mini-2025-01-31",
    api_key=os.environ["OPENAI_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="openai_gpt"
)

gemini_2 = lambda: Automata(
    model_style="openai",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    model_name="gemini-2.0-flash-exp",
    api_key=os.environ["GOOGLE_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="openai_gpt"
)

claude_3 = lambda: Automata(
    model_style="anthropic",
    base_url="https://api.anthropic.com/v1/messages",
    model_name="claude-3-7-sonnet-20250219",
    api_key=os.environ["ANTHROPIC_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="anthropic"
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
    # register a tester and execute it
    Tester(
        tasks_path="./tasks/Raw",
        logs_path="./logs/gpt_4o-raw-textual",
        automata=gpt_4o()
    )()

    # alternative for Tester.__call__()
    # execute tasks one by one immediately
    Tester.plan([
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-screenshot",
            "automata": gpt_4o(),
            "vm_path": os.environ["VM_PATH"],
            "headless": True,
            "obs_types": {OBS.screenshot}
        },
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-a11y_tree",
            "automata": gpt_4o(),
            "vm_path": os.environ["VM_PATH"],
            "headless": True,
            "obs_types": {OBS.a11y_tree}
        },
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-screenshot+a11y_tree",
            "automata": gpt_4o(),
            "vm_path": os.environ["VM_PATH"],
            "headless": True,
            "obs_types": {OBS.screenshot, OBS.a11y_tree}
        },
        {
            "tasks_path": "./tasks/VM",
            "logs_path": "./logs/gpt_4o-vm-set_of_marks",
            "automata": gpt_4o(),
            "vm_path": os.environ["VM_PATH"],
            "headless": True,
            "obs_types": {OBS.set_of_marks}
        }
    ])

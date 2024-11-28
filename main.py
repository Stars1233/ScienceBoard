import sys
import os

sys.dont_write_bytecode = True
from sci import Automata, Tester

gpt_4o = Automata(
    model_style="openai",
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-4o-2024-08-06",
    api_key=os.environ["OPENAI_API_KEY"],
    proxy=os.environ["HTTPX_PROXY"],
    overflow_style="openai_gpt"
)

internvl = Automata(
    model_style="openai",
    base_url=os.environ["LOCAL_BASE_URL"],
    model_name=os.environ["INTERNVL_NAME"],
    overflow_style="openai_lmdeploy"
)

deepseek_vl = Automata(
    model_style="openai",
    base_url=os.environ["LOCAL_BASE_URL"],
    model_name=os.environ["DEEPSEEK_VL_NAME"],
    overflow_style="openai_lmdeploy",
    register=Automata.image_token()
)

qwen_vl = Automata(
    model_style="openai",
    base_url=os.environ["LOCAL_BASE_URL"],
    model_name=os.environ["QWEN_VL_NAME"],
    overflow_style="openai_lmdeploy",
    context_window=2
)


if __name__ == "__main__":
    Tester(
        tasks_path="./tasks/ChimeraX_VM",
        logs_path="./logs/gpt_4o-chimerax-vm-screenshot+a11y_tree",
        vm_path=os.environ["VM_PATH"],
        automata=gpt_4o,
        obs_types={"screenshot", "a11y_tree"}
    )()

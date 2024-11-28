import sys
import os

sys.dont_write_bytecode = True
from sci import Automata, Tester

gpt_4o = Automata(
    model_style="openai",
    base_url="https://api.openai.com/v1/chat/completions",
    model_name="gpt-4o-2024-08-06",
    api_key=os.environ["OPENAI_API_KEY"],
    overflow_style="openai_gpt"
)

internvl = Automata(
    model_style="openai",
    base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
    model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    overflow_style="openai_lmdeploy"
)

deepseek_vl = Automata(
    model_style="openai",
    base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
    model_name="/mnt/workspace/ichinoe/model/deepseek-vl-7b-chat/snapshots/6f16f00805f45b5249f709ce21820122eeb43556",
    overflow_style="openai_lmdeploy"
)

qwen_vl = Automata(
    model_style="openai",
    base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
    model_name="/mnt/workspace/ichinoe/model/Qwen-VL-Chat/snapshots/f57cfbd358cb56b710d963669ad1bcfb44cdcdd8",
    overflow_style="openai_lmdeploy",
    context_window=2
)


if __name__ == "__main__":
    Tester(
        tasks_path="./tasks/ChimeraX_VM",
        logs_path="./logs/gpt_4o-chimerax-vm-screenshot+a11y_tree",
        vm_path="/home/PJLAB/wangyian/Downloads/os-sci/vmware/Ubuntu.vmx",
        automata=gpt_4o,
        obs_types={"screenshot", "a11y_tree"}
    )()

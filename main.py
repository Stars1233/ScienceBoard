import sys

sys.dont_write_bytecode = True
from sci import Automata, Tester

if __name__ == "__main__":
    automata = Automata(
        model_style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/deepseek-vl-7b-chat/snapshots/6f16f00805f45b5249f709ce21820122eeb43556",
        overflow_style="openai_lmdeploy",
        context_window=3,
        register=Automata.image_token()
    )

    Tester(
        tasks_path="./tasks/ChimeraX_VM",
        logs_path="./logs/deepseekvl-chimerax-a11y_tree",
        vm_path="/home/PJLAB/wangyian/Downloads/os-sci/vmware/Ubuntu.vmx",
        automata=automata,
        obs_types={"a11y_tree"}
    )()

import sys

sys.dont_write_bytecode = True
from sci import Automata, Tester

if __name__ == "__main__":
    automata = Automata(
        model_style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
        overflow_style="openai_lmdeploy"
    )

    Tester(
        tasks_path="./tasks/ChimeraX_VM",
        logs_path="./logs",
        vm_path="/home/PJLAB/wangyian/Downloads/os-sci/vmware/Ubuntu.vmx",
        automata=automata,
        debug=True
    )()

VM_USERNAME = "user"
VM_PASSWORD = "password"

# take Lean for instance, a set of optional prompts for a specific app should include following:
#   `LEAN_IS`: RAW / VM, used for brief_intro in APP_INCENTIVE
#   `LEAN_NEED`: RAW ONLY; a generalization of demanded input under Raw sort
#   `LEAN_RAW_USAGE` / `LEAN_VM_USAGE`: RAW / VM, used for exclusive tips; fallback to (`LEAN_TIPS` ?? NULL) if not found
#   `LEAN_RAW_TIPS` / `LEAN_VM_TIPS`: RAW / VM, used for exclusive tips; fallback to (`LEAN_TIPS` ?? NULL) if not found

LEAN_IS = "an interactive theorem prover"
LEAN_NEED = "JSON of Lean REPL"
LEAN_RAW_TIPS = [
    "The proof will be written in tactic mode, and you should apply ONE tactic each time, which returns a integer of proofState with all states stored.",
    "You should submit an JSON with `tactic` and `proofState` (the first proofState is 0), such as `{\"tactic\": \"apply Int.natAbs\", \"proofState\": 0}`"
    "DO NOT forget to attach a field of proofState in the request object or your input will be ignored.",
    "DO NOT submit any Lean 3 code which the compiler of Lean 4 no longer supported."
]

CHIMERAX_IS = "a molecular visualization software"
CHIMERAX_TIPS = [
    "DO NOT introduce any unrelated models or easily close existing models, otherwise the task might be evaluated as FAILED.",
    "DO NOT close the current ChimeraX session, or every effort you made will be in vain.",
    "NEVER try to reopen the command line interface in ChimeraX if it is hidden, because it has been deactivated and cannot do anything. But you are welcome to use it once it is presented."
]

KALGEBRA_IS = "a mathematical graph calculator"
KALGEBRA_TIPS = [
    "Be aware that equations in 3D plotting is a bit different from normal mathematics. For example, the equation `x = y` is actually equivalent to `(x, y) -> x - y`, which means `z = x - y` in KAlgebra."
]

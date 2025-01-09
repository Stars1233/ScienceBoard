VM_USERNAME = "user"
VM_PASSWORD = "password"

# naming criteria: `{TYPE_SORT}_{FIELD}`, take `TYPE_SORT=LEAN_RAW, FIELD=TIPS` for example
# - `TYPE_SORT`: fall back to `LEAN_XXX` if `LEAN_RAW_XXX` does not exist; fall back to default value if `LEAN_XXX` does not exists
# - `FIELD`: act as a padding for reserved slots in PromptFactory
#    - `IS`: a breif introduction of what this application is
#    - `NEED`: a generalization of demanded input
#    - `USAGE`: multiple lines of interaction rules to be explained to models
#    - `TIPS`: additional tips needing extra attention

LEAN_IS = "an interactive theorem prover"
LEAN_RAW_NEED = "JSON of Lean REPL"
LEAN_RAW_TIPS = [
    "The proof will be written in tactic mode, and you should apply ONE tactic each time, which returns a integer of proofState with all states stored.",
    "You should submit an JSON with `tactic` and `proofState` (the first proofState is 0), such as `{\"tactic\": \"apply Int.natAbs\", \"proofState\": 0}`"
    "DO NOT forget to attach a field of proofState in the request object or your input will be ignored.",
    "DO NOT submit any Lean 3 code which the compiler of Lean 4 no longer supported."
]

CHIMERAX_IS = "a molecular visualization software"
CHIMERAX_VM_TIPS = [
    "DO NOT introduce any unrelated models or easily close existing models, otherwise the task might be evaluated as FAILED.",
    "DO NOT close the current ChimeraX session, or every effort you made will be in vain.",
    "NEVER try to reopen the command line interface in ChimeraX if it is hidden, because it has been deactivated and cannot do anything. But you are welcome to use it once it is presented."
]

KALGEBRA_IS = "a mathematical graph calculator"
KALGEBRA_VM_TIPS = [
    "Be aware that equations in 3D plotting is a bit different from normal mathematics. For example, the equation `x = y` is actually equivalent to `(x, y) -> x - y`, which means `z = x - y` in KAlgebra."
]

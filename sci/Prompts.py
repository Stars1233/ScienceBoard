VM_USERNAME = "user"
VM_PASSWORD = "password"

# naming criteria: `{TYPE_SORT}_{FIELD}`, take `TYPE_SORT=LEAN_RAW, FIELD=TIPS` for example
# - `TYPE_SORT`: fall back to `LEAN_XXX` if `LEAN_RAW_XXX` does not exist; fall back to default value if `LEAN_XXX` does not exists
# - `FIELD`: act as a padding for reserved slots in PromptFactory
#    - `IS`: str, a breif introduction of what this application is
#    - `NEED`: str, a generalization of demanded input
#    - `USAGE`: List[str], multiple lines of interaction rules to be explained to models
#    - `TIPS`: List[str], multiple lines of additional tips needing extra attention

LEAN_IS = "an interactive theorem prover"
LEAN_RAW_NEED = "JSON of Lean REPL"
LEAN_RAW_USAGE = [
    "You will be given a unproved theorem declared by `sorry`, which is what you need to prove."
    "Each round you will receive the imports information and initial states together with possible historical interaction records as textual observation, and you are expected to apply EXACTLY ONE tactic as a response.",
    "Your submission should be a JSON with and only with `tactic` and `proofState` fields, such as {\"tactic\": \"apply Int.natAbs\", \"proofState\": 0}`."
    "It is worth noting that the `proofState` which REPL returns contains all proof states stored, so your JSON should also contains this field from which the proof continues."
]
LEAN_RAW_TIPS = [
    "DO NOT forget to attach a field of proofState in the request object, or your input will be ignored.",
    "DO NOT use `sorry` "
    "NEVER submit any Lean 3 code which the compiler of Lean 4 no longer supported."
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

# take ChimeraX for instance, a set of prompts for a specific app should include following
# `${type.upper()}_IS`: optional, used for brief_intro in APP_INCENTIVE
# `${type.upper()}_(RAW|VM)`: optional, used for exclusive tips, fallback to `{type.upper()}` ?? NIL if not found
CHIMERAX_IS = "a molecular visualization software"
CHIMERAX = [
    "DO NOT introduce any unrelated models or easily close existing models, otherwise the task might be evaluated as FAILED;",
    "DO NOT close the current ChimeraX session, or every effort you made will be in vain;",
    "NEVER try to reopen the command line interface in ChimeraX if it is hidden, because it has been deactivated and cannot do anything. But you are welcome to use it once it is presented."
]

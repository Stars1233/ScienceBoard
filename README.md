# OS-SCI

## ENV Config
1. General
    - `VM_PATH`: path to vmware .vmx file
    - `HTTPX_PROXY`: proxy URL; avoid clashes with HTTP_PROXY and HTTPS_PROXY
    - `DEBUG_ERR_FACT`: insert a breakpoint when eval exception occur
2. Models
    - `OPENAI_API_KEY`: API key for OpenAI GPT
    - `QVQ_VL_URL`: Base URL for QVQ
    - `QWEN_VL_URL`: Base URL for QwenVL
    - `INTERN_VL_URL`: Base URL for InternVL
    - `TARS_DPO_URL`: Base URL for UI-Tars
    - `QVQ_VL_NAME`: Name of QVQ
    - `QWEN_VL_NAME`: Name of QwenVL
    - `INTERN_VL_NAME`: Name of InternVL
    - `TARS_DPO_NAME`: Name of UI-Tars
3. Config for raw apps
    - `LEAN_LIB_PATH`: path for Lean 4 REPL
    - `QT6_LIB_PATH`: dynamic library directory for Qt6
    - `FFI_LIB_PATH`: dynamic library file for libffi.so
    - `KALG_BIN_PATH`: executable binary file of KAlgebra
    - `CELE_BIN_PATH`: executable binary file of Celestia
    - `GIS_BIN_PATH`: executable binary file of Grass GIS

# OS-SCI

## ENV Config
1. General
    - `VM_PATH`: path to vmware .vmx file
    - `HTTPX_PROXY`: proxy URL; avoid clashes with HTTP_PROXY and HTTPS_PROXY
    - `DEBUG_ERR_FACT`: insert a breakpoint when eval exception occur
2. Models
    - `OPENAI_API_KEY`: API key for OpenAI GPT
    - `LOCAL_BASE_URL`: base URL for locally deployed model
    - `INTERNVL_NAME`: model name of InternVL
    - `DEEPSEEK_VL_NAME`: model name of DeepSeek-VL
    - `QWEN_VL_NAME`: model name of QWen-VL
3. Raw Apps
    - `QT6_LIB_PATH`: dynamic library directory for Qt6
    - `KALG_BIN_PATH`: executable binary file of KAlgebra

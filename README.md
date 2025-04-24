# OS-SCI

## ENV Config
1. General
    - `VM_PATH`: path to vmware .vmx file
    - `HTTPX_PROXY`: proxy URL; avoid clashes with HTTP_PROXY and HTTPS_PROXY
    - `DEBUG_ERR_FACT`: insert a breakpoint when eval exception occur
2. Models
    - `OPENAI_API_KEY`: API key for OpenAI GPT
    - `GOOGLE_API_KEY`: API key for Google Gemini
    - `ANTHROPIC_API_KEY`: API key for Anthropic Claude
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

## Exceptions
- Error when initializing:

    ```shell
    Traceback (most recent call last):
        File "/usr/lib/python3.11/site-packages/requests/models.py", line 971, in json
            return complexjson.loads(self.text, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/lib/python3.11/json/__init__.py", line 346, in loads
            return _default_decoder.decode(s)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/lib/python3.11/json/decoder.py", line 337, in decode
            obj, end = self.raw_decode(s, idx=_w(s, 0).end())
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/lib/python3.11/json/decoder.py", line 355, in raw_decode
            raise JSONDecodeError("Expecting value", s, err.value) from None
        json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    ```

    the target app has not yet been started up, try to assign a bigger value for 'wait' field.

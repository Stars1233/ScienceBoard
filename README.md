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
    - `QWEN_VL_URL`: Base URL for QwenVL
    - `INTERN_VL_URL`: Base URL for InternVL
    - `QVQ_VL_URL`: Base URL for QVQ
    - `OS_ACT_URL`: Base URL for OS-Atlas
    - `TARS_DPO_URL`: Base URL for UI-Tars
    - `QWEN_VL_NAME`: Name of QwenVL
    - `INTERN_VL_NAME`: Name of InternVL
    - `QVQ_VL_NAME`: Name of QVQ
    - `OS_ACT_NAME`: Name of OS-Atlas
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

- Failed to get accessibility tree:

    ```shell
    Traceback (most recent call last):
        File "os-sci/sci/Tester.py", line 396, in __call__
            counter._pass() if task_info() else counter._fail()
                            ^^^^^^^^^^^
        File "os-sci/sci/Tester.py", line 174, in __call__
            return self.task()
                ^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 175, in _avail_wrapper
            return method(self, *args, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 393, in __call__
            return self.__call()
                ^^^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 381, in __call
            stop_type, stop_args = self.predict()
                                ^^^^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 175, in _avail_wrapper
            return method(self, *args, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/base/log.py", line 462, in record_wrapper
            return_value = method(self)
                        ^^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 316, in predict
            invalid = self._step(step_index)
                    ^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/base/task.py", line 260, in _step
            observation = {
                        ^
        File "os-sci/sci/base/task.py", line 261, in <dictcomp>
            obs_type: getattr(self.manager, obs_type)()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/vm/vmanager.py", line 152, in _env_wrapper
            return method(self, *args, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/base/manager.py", line 85, in _assert_wrapper
            result = method(self)
                    ^^^^^^^^^^^^
        File "os-sci/sci/vm/vmanager.py", line 278, in a11y_tree
            a11y_tree = utils.linearize(raw_a11y_tree)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "os-sci/sci/vm/utils.py", line 206, in linearize
            filtered_nodes = filter_nodes(ET.fromstring(a11y_tree), platform)
                                        ^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/lib/python3.11/xml/etree/ElementTree.py", line 1338, in XML
            parser.feed(text)
        TypeError: a bytes-like object is required, not 'NoneType'
    ```

    input password manually in VMWare and take a new snapshot.

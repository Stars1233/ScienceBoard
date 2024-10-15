from typing import Optional

class Agent:
    def __init__(
        self,
        model_name: str,
        access_token: Optional[str],
        context_window_length: int = 3
    ) -> None:
        self.model_name = model_name
        self.access_token = access_token
        self.context_window_length = context_window_length

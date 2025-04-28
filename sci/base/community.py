import sys

from typing import List, Tuple, Dict
from typing import Optional, Any, Self
from dataclasses import dataclass

sys.dont_write_bytecode = True
from .log import VirtualLog
from .agent import Agent, AIOAgent
from .prompt import TypeSort, CodeLike
from .manager import Manager


@dataclass
class Community:
    def __post_init__(self):
        self.vlog = VirtualLog()

    @property
    def agents(self) -> List[Tuple[str, Agent]]:
        return [
            (key, getattr(self, key))
            for key in self.__dataclass_fields__.keys()
            if isinstance(getattr(self, key), Agent)
        ]

    def __iter__(self) -> Self:
        self.iter_pointer = 0
        return self

    def __next__(self):
        if self.iter_pointer < len(self.agents):
            self.iter_pointer += 1
            return self.agents[self.iter_pointer - 1]
        else:
            raise StopIteration

    def __call__(
        self,
        step_index: int,
        sys_inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort
    ) -> List[CodeLike]:
        raise NotImplementedError


@dataclass
class AllInOne(Community):
    mono: AIOAgent

    def __call__(
        self,
        step_index: int,
        sys_inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort
    ) -> List[CodeLike]:
        init_kwargs = {
            "inst": sys_inst,
            "type_sort": type_sort
        } if step_index == 0 else None

        user_content = self.mono._step(obs, init_kwargs)
        response_message = self.mono(user_content, Manager.HETERO_TIMEOUT)

        assert len(response_message.content) == 1
        response_content = response_message.content[0]

        self.vlog.info(
            f"Response {step_index + 1}/{self.steps}: \n" \
                + response_content.text
        )
        return self.mono.code_handler(response_content, *code_info)


@dataclass
class SeeAct(Community):
    planning: Agent
    grounding: Agent

    def __call__(
        self,
        step_index: int,
        sys_inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort
    ) -> List[CodeLike]:
        # TODO
        raise NotImplementedError

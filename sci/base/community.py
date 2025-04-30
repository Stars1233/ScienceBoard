import sys

from typing import List, Tuple, Dict
from typing import Optional, Any, Self
from dataclasses import dataclass

sys.dont_write_bytecode = True
from .manager import OBS
from .log import VirtualLog
from .agent import Agent, AIOAgent
from .agent import PlannerAgent, GrounderAgent
from .prompt import TypeSort, CodeLike


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
        steps: Tuple[int, int],
        inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort,
        timeout: int
    ) -> List[CodeLike]:
        raise NotImplementedError


@dataclass
class AllInOne(Community):
    mono: AIOAgent

    def __call__(
        self,
        steps: Tuple[int, int],
        inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort,
        timeout: int
    ) -> List[CodeLike]:
        step_index, total_steps = steps
        init_kwargs = {
            "inst": inst,
            "type_sort": type_sort
        } if step_index == 0 else None

        user_content = self.mono._step(obs, init_kwargs)
        response_message = self.mono(user_content, timeout=timeout)

        assert len(response_message.content) == 1
        response_content = response_message.content[0]

        self.vlog.info(
            f"Response {step_index + 1}/{total_steps}: \n" \
                + response_content.text
        )
        return self.mono.code_handler(response_content, *code_info)


@dataclass
class SeeAct(Community):
    planner: PlannerAgent
    grounder: GrounderAgent

    def __call__(
        self,
        steps: Tuple[int, int],
        inst: str,
        obs: Dict[str, Any],
        code_info: tuple[set[str], Optional[List[List[int]]]],
        type_sort: TypeSort,
        timeout: int
    ) -> List[CodeLike]:
        step_index, total_steps = steps
        init_kwargs = {
            "inst": inst,
            "type_sort": type_sort
        } if step_index == 0 else None

        planner_content = self.planner._step(obs, init_kwargs)
        planner_reponse_message = self.planner(planner_content, timeout=timeout)

        assert len(planner_reponse_message.content) == 1
        planner_response_content = planner_reponse_message.content[0]

        self.vlog.info(
            f"Response of planner {step_index + 1}/{total_steps}: \n" \
                + planner_response_content.text
        )

        codes = self.planner.code_handler(planner_response_content, *code_info)
        obs[OBS.schedule] = codes[0].code

        grounder_content = self.grounder._step(obs, init_kwargs)
        grounder_response_message = self.planner(grounder_content, timeout=timeout)

        assert len(grounder_response_message.content) == 1
        grounder_response_content = grounder_response_message.content[0]

        self.vlog.info(
            f"Response of grounder {step_index + 1}/{total_steps}: \n" \
                + grounder_response_content.text
        )
        return self.grounder.code_handler(grounder_response_content, *code_info)

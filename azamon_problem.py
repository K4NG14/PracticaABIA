from typing import Generator

from aima.search import Problem

from azamon_operators import BinPackingOperator
from azamon_state import StateRepresentation


class Azamon(Problem):
    def __init__(self, initial_state: StateRepresentation):
        super().__init__(initial_state)

    def actions(self, state: StateRepresentation) -> Generator[BinPackingOperator, None, None]:
        return state.generate_actions()

    def result(self, state: StateRepresentation, action: BinPackingOperator) -> StateRepresentation:
        return state.apply_action(action)

    def value(self, state: StateRepresentation) -> float:
        return -state.heuristic()

    def goal_test(self, state: StateRepresentation) -> bool:
        return False

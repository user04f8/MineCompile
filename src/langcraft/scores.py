from typing import Literal, Self, List

from .globals import GLOBALS
from .serialize import MiscToken, CommandKeywordToken, TokenBase
from .commands import _OtherCondition, _ConditionType
from .types import _SelectorBase, Objective


class _ScoreOperationCondition(_OtherCondition):
    def __init__(self, target1: _SelectorBase, objective1: Objective, operation: Literal['<', '<=', '=', '>=', '>'],
                 target2: _SelectorBase, objective2: Objective):
        self.target1, self.objective1, self.operation, self.target2, self.objective2 = target1, objective1, operation, target2, objective2
        super().__init__(self, condition_type=_ConditionType.OTHER)

    def sub_tokenize(self) -> List[TokenBase]:
        return [CommandKeywordToken('score'), self.target1, self.objective1, CommandKeywordToken(self.operation),
                self.target2, self.objective2]


class _ScoreMatchesCondition(_OtherCondition):
    def __init__(self, target: _SelectorBase, objective: Objective, match_range: int | str):
        self.target, self.objective, self.range = target, objective, match_range
        super().__init__(self, condition_type=_ConditionType.OTHER)

    def sub_tokenize(self) -> List[TokenBase]:
        return [CommandKeywordToken('score'), self.target, self.objective, CommandKeywordToken('matches'),
                MiscToken(self.range)]


class Score:
    def __init__(self, objective: Objective | str, target: _SelectorBase = _SelectorBase()):
        self.target = target
        if isinstance(objective, str):
            objective = Objective(objective)
        self.objective = objective

    def in_range(self, low: int | str, high: int | str):
        return _ScoreMatchesCondition(self.target, self.objective, f'{low}..{high}')

    def __eq__(self, s: Self | int | str):
        if isinstance(s, int) or isinstance(s, str):
            return _ScoreMatchesCondition(self.target, self.objective, s)
        return _ScoreOperationCondition(self.target, self.objective, '=', s.target, s.objective)

    def __le__(self, s: Self | int):
        if isinstance(s, int):
            return _ScoreMatchesCondition(self.target, self.objective, f'..{s}')
        return _ScoreOperationCondition(self.target, self.objective, '<=', s.target, s.objective)

    def __ge__(self, s: Self):
        if isinstance(s, int):
            return _ScoreMatchesCondition(self.target, self.objective, f'{s}..')
        return _ScoreOperationCondition(self.target, self.objective, '>=', s.target, s.objective)

    def __lt__(self, s: Self):
        return _ScoreOperationCondition(self.target, self.objective, '<', s.target, s.objective)

    def __gt__(self, s: Self):
        return _ScoreOperationCondition(self.target, self.objective, '>', s.target, s.objective)

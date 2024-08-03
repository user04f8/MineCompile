from typing import Literal, Self, List, Tuple

from .base import Statement, Fun, Block, FunStatement, WithStatement
from .commands import Condition, RawExecute, _ConditionArgType
from .scores import Score
from .serialize_types import _Days, _Seconds

class If(WithStatement):
    def __init__(self, condition: _ConditionArgType, add=True):
        super().__init__([], add=add)

        self.condition = condition if isinstance(condition, Condition) else (Condition(condition) if isinstance(condition, str) else Condition(str(condition)))
        self.if_block = Block()
        self.else_block = Block()

    def __call__(self, *statements: Statement | str) -> Self:
        self.if_block = Block(*statements)
        self.if_block.clear()
        if self.condition.always_true:
            self.cmds = self.if_block._get_cmds()
        elif not self.condition.always_false:
            self.cmds += RawExecute.as_cmds(subs=[self.condition], run_statements=self.if_block.statements)
        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
        if self.condition.always_false:
            self.tokens = self.else_block._get_cmds()
        elif not self.condition.always_true:
            self.cmds += RawExecute.as_cmds(subs=[~self.condition], run_statements=self.else_block.statements)
        return self

class While(WithStatement):
    def __init__(self, condition: Condition, add=True):
        super().__init__([], add=add)
        self.condition = condition
    
    def __call__(self, *statements: Statement) -> Self:
        with Fun() as f:
            If(self.condition) (
                *statements,
                f()
            )
        f()
        self.cmds = []
        return None
        # self.cmds = [FunStatement(f)]
        # return self
        
class Do(Statement):
    def __init__(self, *statements: Statement, add=True):
        super().__init__([], add)
        self.statements = statements
    
    def While(self, condition: Condition) -> Self:
        with Fun() as f:
            If(condition) (
                f(),
                self.statements
            )
        self.cmds = [FunStatement(f)]
        return self


class Schedule(WithStatement):
    def __init__(self, time: int | float, time_type: None | Literal['s'] | Literal['d'] = None, add=True):
        super().__init__([], add=add)

        assert time > 0
        if time_type:
            self.time_type = time_type
            self.time = time
        elif time % _Days == 0:
            self.time = time // _Days
            self.time_type = 'd'
        elif time % _Seconds == 0:
            self.time = time // _Seconds
            self.time_type = 's'
        else:
            self.time = time
            self.time_type = ''

    def __call__(self, *statements: Statement) -> Self:
        Fun()(statement for statement in statements)
        self.cmds = []
        # TODO


class ScoreTree(WithStatement):
    def __init__(self, score_key: str, cmds_per_score: int = 1, *, leafs_terminal=False, add=True):
        super().__init__([], add=add)
        self.score = Score(objective=score_key)
        self.cmds_per_score = cmds_per_score
        self.leafs_terminal = leafs_terminal

    def __call__(self, *statements: Statement):
        n = len(statements)
        assert n % self.cmds_per_score == 0
        grouped_statements = [statements[i:i+self.cmds_per_score] for i in range(0, n, self.cmds_per_score)]
        self._generate_tree(grouped_statements)

    def _generate_tree(self, grouped_statements, a=0) -> Tuple[Statement]:
        if len(grouped_statements) == 1:
            return grouped_statements[0]
        n2 = len(grouped_statements) // 2
        with Fun() as f:
            if self.leafs_terminal:
                If(self.score.in_range(a, a + n2 - 1))(
                    *self._generate_tree(grouped_statements[:n2], a)
                )
                self._generate_tree(grouped_statements[n2:], a + n2)
            else:
                If(self.score.in_range(a, a + n2 - 1))(
                    *self._generate_tree(grouped_statements[:n2], a)
                ).Else(
                    *self._generate_tree(grouped_statements[n2:], a + n2)
                )
        return (f(),)

type start = int
type end = int
type iter_amt = int

class For(WithStatement):
    def __init__(self, score_key: str, score_range: start | tuple[start, end] | tuple[start, end, iter_amt], *, add=True):
        super().__init__([], add=add)
        self.score = Score(score_key)
        if isinstance(score_range, int):
            self.score_start = 0
            self.score_end = score_range
            self.iter_by = 1
        elif len(score_range) == 2:
            self.score_start, self.score_end = score_range
            self.iter_by = 1
        elif len(score_range) == 3:
            self.score_start, self.score_end, self.iter_by = score_range
            assert self.iter_by > 0, "iter_amt of score_range = (start, end, iter_amt) must be a positive integer"
        else:
            raise TypeError(f'Invalid arg for score_range: {score_range}')

        self.iter_reverse = self.score_start > self.score_end

    def __call__(self, *statements: Statement):
        self.score.assign(self.score_start)
        call = Fun()(*statements,
                     If((self.score < self.score_end) if self.iter_reverse else (self.score > self.score_end))(
                        # TODO: self.score.add(self.iter_by)
                     ))
        call()

with For('x', (10, 20)):
    pass
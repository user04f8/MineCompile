from typing import Literal

type ObjectiveName = str

class ScoreCompoundCriterion(str):
    pass

type ScoreSettableCriterion = Literal['dummy', 'trigger', 'deathCount', 'playerKillCount', 'totalKillCount']
type ScoreCriterion = ScoreSettableCriterion | Literal['health', 'xp', 'level', 'food', 'air', 'armor'] | ScoreCompoundCriterion

class Int32(int):
    MIN = -2**31
    MAX = 2**31 - 1
    def __init__(self, x: int):
        assert self.MIN <= x <= self.MAX
        super().__init__(x)


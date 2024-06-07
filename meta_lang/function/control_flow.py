from typing import Self, List

from .base import Statement, Fun, Block, TokensContainer
from .commands import Condition, RawExecute
from .debug_utils import *

class If(Statement):
    def __init__(self, condition: Condition | str, add=True):
        super().__init__([], add=add)

        self.condition = (Condition(condition) if isinstance(condition, str) else condition)
        self.if_block = Block()
        self.else_block = Block()
        self.cmds: List[TokensContainer] = []

    def __call__(self, *statements: Statement | str) -> Self:
        self.if_block = Block(*statements)
        self.if_block.clear()
        if self.condition.always_true:
            self.cmds = self.if_block.get_cmds()
        elif not self.condition.always_false:
            self.cmds.append(RawExecute.as_cmd(subs=[self.condition], run_block=self.if_block))
        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
        if self.condition.always_false:
            self.tokens = self.else_block.get_cmds()
        elif not self.condition.always_true:
            self.cmds.append(RawExecute.as_cmd(subs=[~self.condition], run_block=self.else_block))
        return self
        
        



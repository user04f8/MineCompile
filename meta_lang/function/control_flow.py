from typing import Self, List

from .base import Statement, Fun, Block, FunStatement, WithStatement
from .serialize import ParseErrorToken, CommandNameToken
from .commands import Condition, RawExecute
from .debug_utils import *

class If(WithStatement):
    def __init__(self, condition: Condition | str, add=True):
        super().__init__([], add=add)

        self.condition = (Condition(condition) if isinstance(condition, str) else condition)
        self.if_block = Block()
        self.else_block = Block()

    def __call__(self, *statements: Statement | str) -> Self:
        self.if_block = Block(*statements)
        self.if_block.clear()
        if self.condition.always_true:
            self.cmds = self.if_block.get_cmds()
        elif not self.condition.always_false:
            self.cmds += RawExecute.as_cmds(subs=[self.condition], run_block=self.if_block)
        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
        if self.condition.always_false:
            self.tokens = self.else_block.get_cmds()
        elif not self.condition.always_true:
            self.cmds += RawExecute.as_cmds(subs=[~self.condition], run_block=self.else_block).cmds
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


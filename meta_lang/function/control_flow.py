from typing import Self, List
from uuid import uuid4

from .base import Statement, Fun, Block, TokensContainer
from .serialize import ParseErrorToken, CommandNameToken
from .commands import Condition, RawExecute
from .debug_utils import *

class If(Statement):
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

class While(Statement):
    def __init__(self, condition: Condition, add=True):
        super().__init__([], add)
        self.condition = condition
    
    def __call__(self, *statements: Statement) -> Self:
        ref = str(uuid4())
        self.fun = Fun(ref) (
            RawExecute.as_cmd(subs=~self.condition, run_block=CommandNameToken('return')),
            *statements,
            Fun.get_statement(ref).tokenize()
        )
        self.cmds = [
            self.fun
        ]
        return self

class Do(Statement):
    def __init__(self, *statements: Statement, add=True):
        self.fun_ref = Fun() (*statements)
        
        super().__init__([self.fun_ref], add)

    def While(self, condition: Condition) -> Self:
        # if condition.always_true:
        #     return ParseErrorToken('Invalid infinite while loop')
        self.condition = condition

        return self


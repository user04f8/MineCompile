from typing import Tuple, Self, List

from .base import Statement, Condition, Fun, Block, add_cmd
from .serialize import Command, Keyword, Token

class If(Statement):
    def __init__(self, condition: Condition | str):
        self.condition = (Condition(condition) if isinstance(condition, str) else condition)
        self.if_block = Block()
        self.else_block = Block()
        self.idx = add_cmd(self)
        self.cmds = []

    def __call__(self, *statements: Statement | str) -> Self:
        self.if_block = Block(*statements)
        self.if_block.clear()
        if self.condition.always_truthy():
            self.cmds = self.if_block.get_cmds()
        elif not self.condition.always_falsy():
            self.generate_cmd(self.condition, self.if_block)

        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
            # (GLOBAL_CMDS still references self)
        if self.condition.always_falsy():
            self.cmds = self.else_block.get_cmds()
        elif not self.condition.always_truthy():
            self.generate_cmd(~self.condition, self.else_block)
        
        return self
    
    def generate_cmd(self, condition: Condition, block: Block) -> Command:
        if len(self.if_block) == 1:
            self.cmds.append(
                Command(Keyword.EXECUTE, *condition.tokenize(), Keyword.RUN, *block.tokenize())
            )
        elif len(self.if_block) > 1:
            self.cmds.append(
                Command(Keyword.EXECUTE, *condition.tokenize(), Keyword.RUN, Fun()(*block.statements))
            )
        
        # out = ''
        # if len(self.statements) == 1:
        #     out = f'execute {self.condition} run {self.statements[0]}\n'  
        # elif len(self.statements) > 1:
        #     out = f'execute {self.condition} run {Function(*self.statements)}\n'
        # if len(self.else_statements) == 1:
        #     out += f'execute {~self.condition} run {self.statements[0]}\n'
        # elif len(self.else_statements) > 1:
        #     out += f'execute {~self.condition} run {Function(*self.statements)}\n'
        # return out


# def build_statements(statements: List[Statement]) -> str:
#     '\n'.join(f'{statement}' for statement in statements)

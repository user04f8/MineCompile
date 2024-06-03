from typing import Tuple, Self, List

from .base import Statement, Condition, Fun, Block, add_cmd
from .serialize import Command, Keyword, Token

class If(Statement):
    def __init__(self, condition: Condition):
        self.condition = condition
        self.if_block = Block()
        self.else_block = Block()
        self.idx = add_cmd(self)

    def __call__(self, *statements: Statement) -> Self:     
        for statement in statements:
            statement.clear()
        if not self.condition.always_falsy():
            self.if_block = Block(*statements)
            
        return self
    
    def Else(self, *statements: Statement) -> Self:
        for statement in statements:
            statement.clear()
        if not self.condition.always_truthy():
            self.else_block = Block(*statements)
            # (GLOBAL_CMDS still references self)
        
        return self
    
    def get_cmds(self) -> List[Command]:
        if self.condition.always_truthy():
            return self.if_block.get_cmds()
        if self.condition.always_falsy():
            return self.else_block.get_cmds()
        cmds = []
        if len(self.if_block) == 1:
            cmds.append(Command([Keyword.EXECUTE, *self.condition.tokenize(), Keyword.RUN, *self.if_block.tokenize()]))
        elif len(self.if_block) > 1:
            cmds.append(Command([Keyword.EXECUTE, *self.condition.tokenize(), Keyword.RUN, Fun()(*self.if_block.statements)]))
        if len(self.else_block) == 1:
            cmds.append(Command([Keyword.EXECUTE, *(~self.condition).tokenize(), Keyword.RUN, *self.if_block.tokenize()]))
        elif len(self.else_block) > 1:
            cmds.append(Command([Keyword.EXECUTE, *(~self.condition).tokenize(), Keyword.RUN, Fun()(*self.if_block.statements)]))
        
        return cmds
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

from typing import Self, List

from .base import Statement, Fun, Block, TokensContainer
from .commands import Condition, RawExecute

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
            self.gen_cmd(self.condition, self.if_block)

        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
            # (GLOBAL_CMDS still references self)
        if self.condition.always_false:
            self.tokens = self.else_block.get_cmds()
        elif not self.condition.always_true:
            self.gen_cmd(~self.condition, self.else_block)
        
        return self
    
    def gen_cmd(self, condition: Condition, block: Block):
        if len(block) == 1:
            self.cmds.append(RawExecute.as_cmd(condition, *block.single_line_tokenize()))
        elif len(block) > 1:
            self.cmds.append(RawExecute.as_cmd(condition, Fun()(*block.statements)))
        
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

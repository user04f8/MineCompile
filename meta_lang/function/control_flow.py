from typing import Tuple, Self, List

from .base import Statement, Condition, Fun, Block
from .serialize import Command, Keyword, Token

class ExecuteSub:
    pass

class Execute(Statement):
    def __init__(self):
        pass

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
            self.generate_cmd(self.condition, self.if_block)

        return self
    
    def Else(self, *statements: Statement | str) -> Self:
        self.else_block = Block(*statements)
        self.else_block.clear()
            # (GLOBAL_CMDS still references self)
        if self.condition.always_false:
            self.cmds = self.else_block.get_cmds()
        elif not self.condition.always_true:
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

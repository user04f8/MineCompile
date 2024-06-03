from typing import Tuple
from .base import Statement, Conditional, Function, GLOBAL_CMDS, build_statements, add_cmd

class If(Statement):
    def __init__(self, condition: Conditional, *statements: Statement):
        self.condition = condition
        self.statements = statements
        self.else_statements = []
        self.idx = None
        
        
        for statement in self.statements:
            statement.undo()        
        if not self.condition.always_falsy():
            self.idx = add_cmd(self)

    def __str__(self):
        if self.condition.always_truthy():
            return build_statements(self.statements)
        if self.condition.always_falsy():
            return build_statements(self.else_statements)
        out = ''
        if len(self.statements) == 1:
            out = f'execute {self.condition} run {self.statements[0]}\n'  
        elif len(self.statements) > 1:
            out = f'execute {self.condition} run {Function(*self.statements)}\n'
        if len(self.else_statements) == 1:
            out += f'execute {~self.condition} run {self.statements[0]}\n'
        elif len(self.else_statements) > 1:
            out += f'execute {~self.condition} run {Function(*self.statements)}\n'
        return out

    def Else(self, *statements: Statement):
        for statement in statements:
            statement.undo()
        if not self.condition.always_truthy():
            self.else_statements = statements
            # GLOBAL_CMDS[self.idx] = self 


# MetaAutoLangAST
import ast

from ast import literal_eval

from ast import Module, Expression, BinOp, Add, Sub, Mult, Div, Name, Constant, Load, Store


# class CodeLiteral:
#     def __init__(self, value: str) -> None:
#         self.value = value

#     def __repr__(self) -> str:
#         return f'CodeLiteral({repr(self.value)})'

Load = Load()
Store = Store()

import ast
from typing import Any

from malparse import Parser
from malast_types import Code

type Globals = dict[str, Any]

def __CODE__(code_str: str, /):
    return Code(code_str)

class Runtime:
    def __init__(self):
        self.globals: Globals = {} | globals()

    def __str__(self):
        return str(self.globals)

    def get_variable(self, name):
        return self.globals.get(name)

    def set_variable(self, name, value):
        self.globals[name] = value

def postprocess_generated(code: str, variables: Globals):
    for key, value in variables.items():
        code = code.replace(f"${key}$", str(value))
    return code

class Interpreter(ast.NodeVisitor):
    def __init__(self, debug=False):
        self.output = []
        self.runtime = Runtime()
        self.debug = debug

    def generic_visit(self, node):
        if self.debug:
            if node is None:
                print("Encountered a None node")
            else:
                print(f"Generic visit: {node}")
        if not hasattr(node, 'lineno'):
            node.lineno = 0
        if not hasattr(node, 'col_offset'):
            node.col_offset = 0
        
        expression = ast.Expression(body=ast.fix_missing_locations(node))
        
        return eval(compile(expression, '<malpy>', mode='eval'), self.runtime.globals)
        # return super().generic_visit(node)

    def visit_Module(self, node):
        exec(compile(node, '<malpy>', mode='exec'), self.runtime.globals)

        # for stmt in node.body:
        #     out = self.visit(stmt)
        #     if isinstance(out, Code):
        #         self.output.append(out)

    def visit_Expr(self, node: ast.Expr):
        return self.visit(node.value)

    # def visit_Assert(self, node):
    #     assert self.visit(node.test)

    # def visit_BinOp(self, node):
    #     left = self.visit(node.left)
    #     right = self.visit(node.right)
    #     if isinstance(node.op, ast.Add):
    #         return left + right
    #     elif isinstance(node.op, ast.Mult):
    #         return left * right
    #     return self.generic_visit(node)

    # def visit_Name(self, node):
    #     value = self.runtime.get_variable(node.id)
    #     if value is not None:
    #         return value
    #     return eval(node.id, self.runtime.globals)
    #     # return eval(compile(ast.Expression(body=node), '<malpy>', mode='eval'), self.runtime.globals)

    # def visit_Constant(self, node):
    #     return node.value

    # def visit_Assign(self, node):
    #     target = node.targets[0].id
    #     value = self.visit(node.value)
    #     self.runtime.set_variable(target, value)

    # def visit_AugAssign(self, node):
    #     target = node.target.id
    #     op = node.op
    #     value = self.visit(node.value)
    #     if isinstance(op, ast.Add):
    #         self.runtime.set_variable(target, self.runtime.get_variable(target) + value)
    #     elif isinstance(op, ast.Mult):
    #         self.runtime.set_variable(target, self.runtime.get_variable(target) * value)
    #     else:
    #         raise NotImplementedError(f"Operation {type(op)} not implemented")

    # def visit_If(self, node):
    #     if self.visit(node.test):
    #         for stmt in node.body:
    #             self.visit(stmt)
    #     else:
    #         for stmt in node.orelse:
    #             self.visit(stmt)

    # def visit_For(self, node):
    #     for value in self.visit(node.iter):
    #         self.runtime.set_variable(node.target.id, value)
    #         print(f'set var {node.target.id}={value}')
    #         for stmt in node.body:
    #             self.visit(stmt)
    #     else:
    #         for stmt in node.orelse:
    #             self.visit(stmt)

    # def visit_Call(self, node: ast.Call):
    #     return self.visit(node.func)(*(self.visit(arg) for arg in node.args), **{keyword.arg: self.visit(keyword.value) for keyword in node.keywords})

    # def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
    #     pass # TODO
    #     node.args.posonlyargs

    def generate_code(self, node):
        self.visit(node)
        out = '\n'.join(self.output)
        out = postprocess_generated(out, self.runtime.globals)
        return out

def parse_interp(filename):
    parser = Parser()
    with open(filename) as file:
        code = file.read()

    tree = parser.parse(code, filename, debug=1)

    code_generator = Interpreter(debug=True)

    generated_code = code_generator.generate_code(tree)

    print(generated_code)

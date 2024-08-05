import ast
from typing import Any

from malparse import Parser
from malast_types import Code

type Variables = dict[str, Any]

class Runtime:
    def __init__(self):
        self.variables: Variables = {}

    def __str__(self):
        return str(self.variables)

    def get_variable(self, name):
        return self.variables.get(name)

    def set_variable(self, name, value):
        self.variables[name] = value

def replace_variables(code: str, variables: Variables):
    for key, value in variables.items():
        code = code.replace(f"${key}$", str(value))
    return code

class Interpreter(ast.NodeVisitor):
    def __init__(self, debug=False):
        self.output = []
        self.runtime = Runtime()
        self.debug = debug

    def visit(self, node):
        if self.debug:
            print(f"Visiting node: {node})")
        return super().visit(node)

    def generic_visit(self, node):
        if self.debug:
            if node is None:
                print("Encountered a None node")
            else:
                print(f"Generic visit: {node}")
        return super().generic_visit(node)

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Expr(self, node: ast.Expr):
        out = self.visit(node.value)
        if isinstance(out, Code):
            self.output.append(out)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        # if isinstance(node.op, ast.Add):
        #     return left + right
        # elif isinstance(node.op, ast.Mult):
        #     return left * right
        return self.generic_visit(node)

    def visit_Name(self, node):
        return self.runtime.get_variable(node.id)

    def visit_Constant(self, node):
        return node.value

    def visit_Assert(self, node):
        assert self.visit(node.test)

    def visit_Assign(self, node):
        target = node.targets[0].id
        value = self.visit(node.value)
        self.runtime.set_variable(target, value)


    def visit_AugAssign(self, node):
        target = node.target.id
        op = node.op
        value = self.visit(node.value)
        if isinstance(op, ast.Add):
            self.runtime.set_variable(target, self.runtime.get_variable(target) + value)
        elif isinstance(op, ast.Mult):
            self.runtime.set_variable(target, self.runtime.get_variable(target) * value)
        else:
            raise NotImplementedError(f"Operation {type(op)} not implemented")

    def visit_If(self, node):
        if self.visit(node.test):
            for stmt in node.body:
                self.visit(stmt)
        else:
            for stmt in node.orelse:
                self.visit(stmt)

    def generate_code(self, node):
        self.visit(node)
        out = '\n'.join(self.output)
        out = replace_variables(out, self.runtime.variables)
        return out

def parse_interp(filename):
    parser = Parser()
    with open(filename) as file:
        code = file.read()

    tree = parser.parse(code, filename, debug=1)

    code_generator = Interpreter(debug=False)
    code_generator.runtime.set_variable('x', 1)

    # Generate code
    generated_code = code_generator.generate_code(tree)

    print(code_generator.runtime)

    # Output the generated code
    print(generated_code)

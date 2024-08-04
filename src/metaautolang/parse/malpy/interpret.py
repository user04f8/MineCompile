import ast

from malparse import Parser

EXAMPLE_FILENAME = 'example.mcpy'

class Runtime:
    def __init__(self):
        self.variables = {}

    def get_variable(self, name):
        return self.variables.get(name)

    def set_variable(self, name, value):
        self.variables[name] = value

class Interpreter(ast.NodeVisitor):
    def __init__(self):
        self.output = []
        self.runtime = Runtime()

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Expression(self, node):
        self.visit(node.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Mult):
            return left * right
        # Add more operators as needed

    def visit_Name(self, node):
        return self.runtime.get_variable(node.id)  # Or fetch from a symbol table if needed

    def visit_Constant(self, node):
        return node.value

    def visit_CodeLiteral(self, node):
        self.output.append(node.value)
        return node.value

    def visit_Assert(self, node):
        assert self.visit(node.test)

    def generate_code(self, node):
        self.visit(node)
        return '\n'.join(self.output)
    

if __name__ == '__main__':
    parser = Parser()
    with open(EXAMPLE_FILENAME) as file:
        tree = parser.parse(file)

    code_generator = Interpreter()
    code_generator.runtime.set_variable('x', 1)

    # Generate code
    generated_code = code_generator.generate_code(tree)

    # Output the generated code
    print(generated_code)
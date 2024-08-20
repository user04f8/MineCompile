import ast
from typing import Any

from malparse import Parser
from malast_types import Code, CodeHook

type Globals = dict[str, Any]

def __CODE__(code_str: str, /):
    return Code(code_str)

OUTPUT_CATCH_IDENT = '$add_to_output'

class Runtime:
    def __init__(self):
        self.output = []
        def add_to_output_if_code(value):
            if isinstance(value, Code):
                self.output.append(str(value))
            return value
        
        def add_hook(hook_id, assignment_value=None):
            # NOTE: assignment_value appears to do nothing but is relied on existing from the malpy.gram parser
            self.output.append(CodeHook(hook_id))

        self.globals: Globals = {
            '__CODE__': __CODE__,
            '__HOOK__': add_hook,
            OUTPUT_CATCH_IDENT: add_to_output_if_code
        }

    def __str__(self):
        return str(self.globals)

    

def postprocess_generated(code: str, variables: Globals):
    for key, value in variables.items():
        code = code.replace(f"${key}$", str(value))
    return code

class CodeTransformer(ast.NodeTransformer):
    def __init__(self):
        self.runtime = Runtime()

    def __call__(self, tree):
        transformed_tree = self.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        code = compile(transformed_tree, filename="<malpy>", mode="exec")
        exec(code, self.runtime.globals)

        print(self.runtime.output)

        for i, out in enumerate(self.runtime.output):
            if isinstance(out, str):
                pass
            elif isinstance(out, CodeHook):
                val = self.runtime.globals.get(out.ident)
                if val is None:
                    self.runtime.output[i] = ''
                else:
                    self.runtime.output[i] = val
            else:
                raise TypeError()
            
        print(self.runtime.output)

        return '\n'.join(self.runtime.output)

    def visit_Expr(self, node):
        new_node = ast.Expr(
            value=ast.Call(
                func=ast.Name(id=OUTPUT_CATCH_IDENT, ctx=ast.Load()),
                args=[node.value],
                keywords=[]
            )
        )
        return ast.copy_location(new_node, node)

def parse_interp(filename):
    parser = Parser()
    with open(filename) as file:
        code = file.read()

    tree = parser.parse(code, filename, debug=1)

    code_transformer = CodeTransformer()

    transformer = CodeTransformer()
    autogened_code = transformer(tree)
    
    print(autogened_code)

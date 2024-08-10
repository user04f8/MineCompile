import ast
from malast_types import Code 

output = []

def __CODE__(code_str: str):
    return Code(code_str)

def add_to_output_if_code(value):
    if isinstance(value, Code):
        output.append(str(value))
    return value

class CodeTransformer(ast.NodeTransformer):
    def visit_Expr(self, node):
        new_node = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='add_to_output_if_code', ctx=ast.Load()),
                args=[node.value],
                keywords=[]
            )
        )
        return ast.copy_location(new_node, node)

def standalone_interpret(source_code):
    global output
    output = []  # Reset the output for each run
    tree = ast.parse(source_code)
    transformer = CodeTransformer()
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    # Compile and execute the transformed code
    code = compile(transformed_tree, filename="<malpy>", mode="exec")
    exec(code, {'__CODE__': __CODE__, 'add_to_output_if_code': add_to_output_if_code})

if __name__ == '__main__':
    source_code = """
    for _ in range(3):
        __CODE__("test")
    """

    standalone_interpret(source_code)
    print(output)

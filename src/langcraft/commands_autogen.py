from copy import deepcopy
from keyword import kwlist
import re


ALIASES = {
    
}

def camel_to_snake(camel_str):
    # Replace all capital letters with underscore followed by the lowercase version of the letter
    snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    return snake_str

def pythonize_name(name: str) -> str:
    if name in ALIASES:
        return ALIASES[name]
    if name in kwlist:
        return name + '_'
    return name

class Literal:
    def __init__(self, *args):
        self.args = args

    def __class_getitem__(self, args):
        return self(*args)

    def __str__(self):
        return f'Literal[{", ".join(repr(arg) for arg in self.args)}]'

type CommandType = type | Literal | str | list[CommandType]

class Args:
    def __init__(self, **kwargs: CommandType):
        self.args: dict[str, CommandType] = kwargs
        self.next_command_def = {}

    def __add__(self, command_def):
        self.next_command_def = command_def

    def arg_strs(self) -> list[tuple[str, str, str]]:
        def arg_str(arg_type):
            if isinstance(arg_type, list):
                return 'Optional[' + arg_str(arg_type[0]) + '] = None'
            elif isinstance(arg_type, str):
                return arg_type
            elif isinstance(arg_type, Literal):
                return str(arg_type)
            else:
                return arg_type.__name__

        return [(camel_to_snake(arg_name), arg_str(arg_type), arg_type) for arg_name, arg_type in self.args.items()]

type CommandDef = dict[str, CommandDef | None | Args]

COMMANDS: CommandDef = {
    'scoreboard': {
        'objectives': {
            'list': None,
            'add': Args(objective=str, criteria=str, displayName=[str]),
            'remove': Args(objective=str)
        }
    }
}

class CodeStr(list):
    INDENT = '    '
    def __init__(self, x: str | None = None):
        super().__init__([] if x is None else [x])
        self.indent_level = 0
    
    def __enter__(self):
        self.indent_level += 1

    def __exit__(self, *args):
        self.indent_level -= 1

    def append(self, x: str):
        super().append(self.INDENT * self.indent_level + x)

    def newline(self, n=1):
        for _ in range(n):
            super().append('')

    def __str__(self):
        return '\n'.join(self)


if __name__ == '__main__':
    code = CodeStr()
    for command, command_def in COMMANDS.items():
        code = CodeStr(f'class {command.capitalize()}(StructuredCommand):')
        with code:
            code.append(f"NAME = '{command}'")
            code.newline()

            def is_final(command_def):
                if command_def is None:
                    return True
                if isinstance(command_def, dict):
                    return False
                if isinstance(command_def, Args):
                    return not command_def.next_command_def
                raise TypeError(type(command_def))

            def tokenize_args(args):
                def tokenize_arg(arg_name, arg_type_str, arg_type):
                    if arg_type is str:
                        code.append(f"self._add_token(StrToken({arg_name}))")
                    else:
                        code.append(f"self._add_token({arg_type_str}({arg_name}))")
                for arg_name, arg_type_str, arg_type in args:
                    if isinstance(arg_type, list):
                        arg_type = arg_type[0]
                        code.append(f'if {arg_name} is not None:')
                        with code:
                            tokenize_arg(arg_name, arg_type_str, arg_type)
                    else:
                        tokenize_arg(arg_name, arg_type_str, arg_type)
                    
            def parse_subcommands(command_def, root=False, args=None):
                if args is None:
                    args = []

                for subcommand, subcommand_def in command_def.items():
                    subcommand_args = deepcopy(args)  # Reset args for each subcommand
                    self_str = 'self'
                    if root:
                        self_str = 'cls'
                        code.append('@classmethod')
                    if isinstance(subcommand_def, Args):
                        if subcommand_def.next_command_def:
                            subcommand_args += subcommand_def.arg_strs()
                        else:
                            subcommand_args += subcommand_def.arg_strs()
                            code.append(f'def {pythonize_name(subcommand)}({self_str}, {", ".join(f"{arg_name}: {arg_type_str}" for arg_name, arg_type_str, _ in subcommand_args)}):')
                    else:
                        code.append(f'def {pythonize_name(subcommand)}({self_str}):')
                    with code:
                        if root:
                            if is_final(subcommand_def):
                                code.append(f"self = cls('{pythonize_name(subcommand)}')")
                                tokenize_args(subcommand_args)
                                code.append(f"self._finalize()")
                                code.append(f"return self")
                            else:
                                code.append(f"return cls('{pythonize_name(subcommand)}')")
                        else:
                            code.append(f"self._add_kw('{subcommand}')")
                            if is_final(subcommand_def):
                                tokenize_args(subcommand_args)
                                code.append(f"self._finalize()")
                            code.append(f"return self")
                    code.newline()

                    subcommand_def = subcommand_def.next_command_def if isinstance(subcommand_def, Args) else subcommand_def
                    if subcommand_def is not None:
                        parse_subcommands(subcommand_def, args=subcommand_args)

            if command_def is None:
                pass
            elif isinstance(command_def, dict):
                parse_subcommands(command_def, root=True)
            else:
                raise TypeError()

        print(str(code))

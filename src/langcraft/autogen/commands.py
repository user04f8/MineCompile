from copy import deepcopy
from keyword import kwlist

from .mc_syntax import COMMANDS, Args, Literal, Alias

# py -m langcraft.autogen.commands

FILENAME = 'langcraft/autogened_commands.py'

ALIASES = {}

def pythonize_name(name: str | Alias) -> str:
    if isinstance(name, Alias):
        return name.python_name
    if name in ALIASES:
        return ALIASES[name]
    if name in kwlist:
        return name + '_'
    return name

def mc_name(name: str | Alias) -> str:
    if isinstance(name, Alias):
        return name.mc_name
    return name


class CodeStr(list):
    INDENT = '    '
    def __init__(self, x: str):
        super().__init__([x])
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
    code = CodeStr(
'''from typing import Optional, Literal

from .serialize import StrToken
from .commands import StructuredCommand
'''
    )
    for command, command_def in COMMANDS.items():
        code.append(f'class {command.capitalize()}(StructuredCommand):')
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
                    elif isinstance(arg_type, Literal):
                        code.append(f"self._add_kw({arg_name})")
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
                        if is_final(subcommand_def):
                            code.append('@classmethod')
                        else:
                            code.append('@classmethod')
                            code.append('@property')
                    elif not is_final(subcommand_def):
                        code.append('@property')

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
                                code.append(f"self = cls('{mc_name(subcommand)}')")
                                tokenize_args(subcommand_args)
                                code.append(f"self._finalize()")
                                code.append(f"return self")
                            else:
                                code.append(f"return cls('{mc_name(subcommand)}')")
                        else:
                            if mc_name(subcommand):
                                code.append(f"self._add_kw('{mc_name(subcommand)}')")
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
    out = str(code)
    print(out)

    if input(f'save to {FILENAME} (Y/n) ') in ('y', ''):
        with open(FILENAME, 'w') as f:
            print('writing. . .')
            f.write(out)
            print('done!')
    else:
        print('canceled by user')

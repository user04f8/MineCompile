from copy import deepcopy
from keyword import kwlist

from langcraft.autogen.mc_syntax import COMMANDS, Args, Literal, Alias

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
    exiting = False

    def __init__(self, x: str):
        super().__init__([x])
        self.indent_level = 0
    
    def __enter__(self):
        self.indent_level += 1
        CodeStr.exiting = False

    def __exit__(self, *args):
        self.indent_level -= 1
        if not CodeStr.exiting:
            self.newline()
        CodeStr.exiting = True

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

from .serialize import StrToken, BoolToken, CommandKeywordToken
from .commands import StructuredCommand
from .mutables import Entities
'''
    )

    code.append(f'__all__ = ({', '.join(f"'{pythonize_name(cmd).capitalize()}'" for cmd in COMMANDS)})')
    code.newline()

    def is_final(command_def):
        if command_def is None:
            return True
        if isinstance(command_def, dict):
            return False
        if isinstance(command_def, Args):
            return not command_def.next_command_def
        raise TypeError(type(command_def))
    
    def parse_subcommands(root_command_name, command_def, args: list[tuple[str, str, str]] = None, format = None):
        if args is None:
            args = []
        if format is None:
            format = []

        for command, command_def in command_def.items():
            sub_args = deepcopy(args)
            if mc_name(command) is None:
                sub_format = deepcopy(format)
            else:
                sub_format = deepcopy(format) + [mc_name(command)]

            if isinstance(command_def, Args):
                for arg_tuple in command_def.arg_strs():
                    sub_format.append('$arg')
                    sub_args.append(arg_tuple)
                
                command_def = command_def.next_command_def

            if pythonize_name(command) is None:
                assert is_final(command_def), "Cannot have None as key in non-final context"

                if sub_args:
                    code.append(f'def __call__(self, {", ".join(f"{arg_name}: {arg_type_str}" for arg_name, arg_type_str, _ in sub_args)}):')
                else:
                    code.append(f'def __call__(self):')
                with code:
                    code.append(f'self._finalize([{", ".join(arg_name for arg_name, _, _ in sub_args)}])')
            else:
                if is_final(command_def):
                    class_name = f"__{pythonize_name(command)}"
                    code.append(f"class {class_name}(StructuredCommand):")
                else:
                    class_name = f"{pythonize_name(command)}"
                    code.append(f"class {class_name}(StructuredCommand):")
                with code:
                    if is_final(command_def):
                        code.append(f"NAME = '{root_command_name}'")
                        code.append(f"FORMAT = {str(sub_format)}")

                    if command_def is None:
                        pass
                    elif isinstance(command_def, dict):
                        parse_subcommands(root_command_name, command_def, args=sub_args, format=sub_format)
                    else:
                        raise TypeError()
                
                if is_final(command_def):
                    code.append(f'@classmethod')
                    if sub_args:
                        code.append(f'def {pythonize_name(command)}(cls, {", ".join(f"{arg_name}: {arg_type_str}" for arg_name, arg_type_str, _ in sub_args)}):')
                    else:
                        code.append(f'def {pythonize_name(command)}(cls):')
                    with code:
                        def arg_type_to_str(arg_type, arg_name) -> str:
                            if isinstance(arg_type, list):
                                return f'(None if {arg_name} is None else {arg_type_to_str(arg_type[0], arg_name)})'
                            if arg_type is str:
                                return f'StrToken({arg_name})'
                            if arg_type is bool:
                                return f'BoolToken({arg_name})'
                            if isinstance(arg_type, Literal):
                                return f'CommandKeywordToken({arg_name})'
                            return arg_name
                            # return f'{arg_type}({arg_name})'  # if casting is necessary
                        code.append(f'return cls.{class_name}()._finalize([{", ".join(arg_type_to_str(arg_type, arg_name) for arg_name, _, arg_type in sub_args)}])')
                    

    for command, command_def in COMMANDS.items():
        class_name = f"{pythonize_name(command).capitalize()}"
        code.append(f"class {class_name}{('(StructuredCommand)' if is_final(command_def) else '')}:")
        format = []
        args = []
        
        if isinstance(command_def, Args):
            for arg_tuple in command_def.arg_strs():
                format.append(None)
                args.append(arg_tuple)
            
            command_def = command_def.next_command_def
        with code:
            if command_def is None:
                pass
            elif isinstance(command_def, dict):
                parse_subcommands(command, command_def, args=args, format=format)
            else:
                raise TypeError()
        code.newline()
            

    out = str(code)
    print(out)

    if input(f'save to {FILENAME} (y/n) ') in ('y', ''):
        with open(FILENAME, 'w') as f:
            print('writing. . .')
            f.write(out)
            print('done!')
    else:
        print('canceled by user')

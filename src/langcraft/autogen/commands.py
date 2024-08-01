from copy import deepcopy
from keyword import kwlist
from types import UnionType
from typing import get_origin, Literal, Union

from langcraft.autogen.mc_syntax import COMMANDS, Args, Alias

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

    @staticmethod
    def _preprocess(x: str) -> str:
        return x.replace('typing.', '')

    def append(self, x: str):
        super().append(self.INDENT * self.indent_level + self._preprocess(x))

    def newline(self, n=1):
        for _ in range(n):
            super().append('')

    def __str__(self):
        return '\n'.join(self)


def _autogen():
    code = CodeStr(
'''
from typing import Optional, Literal, Union

from .serialize import StrToken, BoolToken, IntToken, FloatToken, MiscToken, CommandKeywordToken
from .serialize_types import ResourceLocation
from .commands import StructuredCommand
from .mutables import Entities, SingleEntity, Players, SinglePlayer
from .minecraft_builtins import EffectType, EntityType, BlockType, _AttributeType

def resource_location_cast(x: str | ResourceLocation) -> ResourceLocation:
    if isinstance(x, str):
        return ResourceLocation('minecraft', x)
    return x
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
    
    def finalize_call(sub_args):
        def arg_type_to_str(arg_type, arg_name) -> str:
            if isinstance(arg_type, list):
                assert len(arg_type) == 1
                return f'(None if {arg_name} is None else {arg_type_to_str(arg_type[0], arg_name)})'
            elif arg_type is str:
                return f'StrToken({arg_name})'
            elif arg_type is bool:
                return f'BoolToken({arg_name})'
            elif arg_type is int:
                return f'IntToken({arg_name})'
            elif arg_type is float:
                return f'FloatToken({arg_name})'
            elif arg_type == 'ResourceLocation':
                return f'resource_location_cast({arg_name})'
            elif get_origin(arg_type) in (Union, UnionType):
                return f'MiscToken({arg_name})'
            elif get_origin(arg_type) == Literal:
                return f'CommandKeywordToken({arg_name})'
            elif isinstance(arg_type, str):
                return arg_name
            else:
                return f'MiscToken({arg_name})'

        return f'_finalize([{", ".join(arg_type_to_str(arg_type, arg_name) for arg_name, _, arg_type in sub_args)}], add=add)'
    
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
                    _, _, arg_type = arg_tuple
                    sub_format.append('$optional_arg' if isinstance(arg_type, list) else '$arg')
                    sub_args.append(arg_tuple)
                
                command_def = command_def.next_command_def

            if pythonize_name(command) is None:
                assert is_final(command_def), "Cannot have None as key in non-final context"

                if sub_args:
                    code.append(f'def __init__(self, {", ".join(f"{arg_name}: {arg_type_str}" for arg_name, arg_type_str, _ in sub_args)}, add=True):')
                else:
                    code.append(f'def __init__(self, add=True):')
                with code:
                    code.append(f'self.{finalize_call(sub_args)}')
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
                    elif None in command_def.keys():
                        code.append(f"NAME = '{root_command_name}'")
                        sub_format_ = sub_format
                        command_def_ = command_def[None]
                        if isinstance(command_def_, Args):
                            for _, _, arg_type in command_def_.arg_strs():
                                sub_format_.append('$optional_arg' if isinstance(arg_type, list) else '$arg')
                        code.append(f"FORMAT = {str(sub_format_)}")

                    if command_def is None:
                        pass
                    elif isinstance(command_def, dict):
                        parse_subcommands(root_command_name, command_def, args=sub_args, format=sub_format)
                    else:
                        raise TypeError()
                
                if is_final(command_def):
                    code.append(f'@classmethod')
                    if sub_args:
                        code.append(f'def {pythonize_name(command)}(cls, {", ".join(f"{arg_name}: {arg_type_str}" for arg_name, arg_type_str, _ in sub_args)}, add=True):')
                    else:
                        code.append(f'def {pythonize_name(command)}(cls, add=True):')
                    with code:
                        
                        code.append(f'return cls.{class_name}().{finalize_call(sub_args)}')
                    

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


if __name__ == '__main__':
    _autogen()
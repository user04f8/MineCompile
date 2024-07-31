import re

def camel_to_snake(camel_str):
    # Replace all capital letters with underscore followed by the lowercase version of the letter
    snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
    return snake_str

class Alias:
    def __init__(self, python_name, mc_name):
        self.mc_name = mc_name
        self.python_name = python_name

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
        self.next_command_def: dict | None = None

    def __add__(self, command_def):
        self.next_command_def = command_def
        return self

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
            'remove': Args(objective=str),
            Alias('set_display', 'setdisplay'): Args(slot=str, objective=[str]),
            'modify': Args(objective=str) + {
                Alias('display_auto_update', 'displayautoupdate'): Args(value=bool),
                Alias('display_name', 'displayname'): Args(displayName=str),
                Alias('number_format', 'numberformat'): {
                    Alias('reset', None): None,
                    'blank': None,
                    'fixed': Args(component=str),
                    'styled': Args(style=str)
                },
                'rendertype': Args(rendertype=Literal['hearts', 'integer'])
            }
        }
    },
    'effect': {
        'clear': Args(targets=[str], effect=[str]),
        'give': Args(targets='Entities', effect=str) + {
            None: Args(seconds=[int], amplifier=[int], hideParticles=[bool]),
            'infinite': Args(amplifier=[int], hideParticles=[bool])
        }
    }
}
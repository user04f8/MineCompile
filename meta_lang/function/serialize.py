from typing import Tuple, List, Self
from uuid import uuid4
from itertools import product
from enum import StrEnum

class StrToken:
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s
    
class CommandToken(StrToken):
    pass

class CommandSubToken(StrToken):
    pass

class FunctionToken:
    def __init__(self, namespace: str, path: List[str]):
        self.namespace = namespace
        self.path = path

    def __str__(self):
        return f'function {self.namespace}:{'/'.join(self.path)}'

# class CommandName(type, StrToken):
#     NAMES = []

#     def __init__(self, x):
#         if x in self.NAMES:
#             pass
    
#     def __new__(mcs, name, base, dct):
#         CommandName.NAMES.append(name)

#         cls = super().__new__(mcs, name, base, dct)
#         return cls

class Keyword(StrEnum):
    EXECUTE = 'execute'
    IF = 'if'
    UNLESS = 'unless'
    RUN = 'run'

class CommandSepToken:
    def __init__(self):
        pass

    def __str__(self):
        return '\n'

class Choice:
    def __init__(self, choices: Tuple[str], ident=None):
        self.choices = choices
        self.ident = ident
        if self.ident is None:
            self.uuid = uuid4()
            self.ident = str(self.uuid)

    def __hash__(self):
        if self.ident is None:
            return self.uuid.int
        else:
            return hash(self.ident)
        
    def __str__(self):
        return f'$choice[{self.ident}]({self.choices})$'

class Selector:
    def __init__(self, s: str = 's', **kwargs):
        # TODO structure kwargs by https://minecraft.wiki/w/Target_selectors
        assert s in {'p', 'r', 'a', 'e', 's', 'n'}
        self.s = s
        self.kwargs = kwargs

    def __str__(self):
        return f'@{self.s}[{','.join(f"{key}={val}" for key, val in self.kwargs.items())}]'

class EntitySelector(Selector):
    def __init__(self, **kwargs):
        return Selector('e', **kwargs)

class VarToken:
    def __init__(self, entity_ref: Selector, name):
        self.entity_ref = entity_ref,
        self.name = name

    def __str__(self):
        return f'$var[{self.entity_ref}][{self.name}]$'

Token = StrToken | Keyword | Choice | Selector | VarToken | CommandSepToken

class Command:
    def __init__(self, *tokens: Token):
        self.tokens = tokens

    def __str__(self):
        # return ' '.join(str(token) for token in self.tokens)

        assignments = {
            choice.ident: choice.choices
                for choice in set(
                    choice for choice in self.tokens if isinstance(choice, Choice)
                )
        }

        combinations = list(product(*assignments.values()))

        command_choices = []
        for combination in combinations:
            command_choice = []
            for token in self.tokens:
                if isinstance(token, Choice):
                    index = list(assignments.keys()).index(token.ident)
                    command_choice.append(combination[index])
                else:
                    command_choice.append(str(token))
            command_choices.append(' '.join(command_choice))

        return '\n'.join(command_choices)

class CommandRef:
    def get_cmds(self) -> List[Command | Self]:
        return []
    
    def __str__(self):
        return '\n'.join(
            str(cmd) for cmd in self.resolve()
        )
    
    def resolve(self) -> List[Command]:
        return [(cmd.resolve() if isinstance(cmd, CommandRef) else cmd) for cmd in self.get_cmds()]


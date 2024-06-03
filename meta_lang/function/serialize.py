from typing import Tuple, List
from uuid import uuid4
from itertools import product
from enum import StrEnum

class StrToken:
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s


class FunctionToken:
    def __init__(self, namespace: str, path: List[str]):
        self.namespace = namespace
        self.path = path

    def __str__(self):
        return f'function {self.namespace}:{'/'.join(self.path)}'

class Keyword(StrEnum):
    EXECUTE = 'execute'
    IF = 'if'
    UNLESS = 'unless'
    RUN = 'run'

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

Token = StrToken | Keyword | Choice

class Command:
    def __init__(self, tokens=[]):
        self.tokens: List[Token] = tokens

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

    def add(self, token: Token):
        self.tokens.append(token)

Program = List[Command]


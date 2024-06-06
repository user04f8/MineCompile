from typing import Tuple, List, Self
from uuid import uuid4
from itertools import product
from enum import StrEnum

from termcolor import colored

class SubToken:
    def __init__(self):
        pass

    def __str__(self) -> str:
        raise NotImplementedError
    
    def __format__(self, format_spec: str) -> str:
        return str(self)

# TOKENS

class Token:
    def __init__(self):
        pass

    def __str__(self) -> str:
        raise NotImplementedError
    
    def color_str(self) -> str:
        return self.__str__()
    
    def debug_str(self) -> str:
        return self.color_str()
    
    def __format__(self, format_spec: str) -> str:
        return str(self)
    
class Serializable(Token):
    def __init__(self):
        self.token: Token
    
    def __str__(self):
        return self.token.__str__()
    
class StrToken(Token):
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s
    
    def color_str(self) -> str:
        return colored(self.__str__(), 'green')
    
class CommandNameToken(StrToken):
    def color_str(self) -> str:
        return colored(self.__str__(), 'magenta', attrs=["bold"])

class CommandKeywordToken(StrToken):
    def color_str(self) -> str:
        return colored(self.__str__(), 'magenta')

class FunctionToken(Token):
    def __init__(self, namespace: str, path: List[str]):
        self.namespace = namespace
        self.path = path

    def __str__(self):
        return f'function {self.namespace}:{'/'.join(self.path)}'
    
    def color_str(self):
        return colored(self.__str__(), 'magenta', attrs=["bold"])

# class CommandName(type, StrToken):
#     NAMES = []

#     def __init__(self, x):
#         if x in self.NAMES:
#             pass
    
#     def __new__(mcs, name, base, dct):
#         CommandName.NAMES.append(name)

#         cls = super().__new__(mcs, name, base, dct)
#         return cls

class KeywordToken(Token):
    EXECUTE = CommandNameToken('execute')
    IF = CommandKeywordToken('if')
    UNLESS = CommandKeywordToken('unless')
    RUN = CommandKeywordToken('run')

TOKEN_SEP = ' '
COMMAND_SEP = '\n'

class CommandSepToken(Token):
    def __str__(self):
        return COMMAND_SEP

class ChoiceSpecialToken(Token):
    """
    Defines a set of potential values to duplicate a list of tokens over

    Example usage:
    [
        [a, b, Choice(c, d)],
        [e, f]
    ]
    -->
    [
        [a, b, c],
        [a, b, d],
        [e, f]
    ]
    """
    def __init__(self, *choices: Token | List[Token], ident=None):
        self.choices = tuple(([choice] if isinstance(choice, Token) else choice) for choice in choices)
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

class SelectorToken(Token):
    def __init__(self, s: str = 's', **kwargs):
        # TODO structure kwargs by https://minecraft.wiki/w/Target_selectors
        assert s in {'p', 'r', 'a', 'e', 's', 'n'}
        self.s = s
        self.kwargs = kwargs

    def __str__(self):
        return f'@{self.s}[{','.join(f"{key}={val}" for key, val in self.kwargs.items())}]'

class TokensContainer:
    def __init__(self, *tokens: Token):
        self.tokens = tokens

    def __iter__(self):
        return self.tokens.__iter__()
    
    def tokenize(self):
        return list(self.tokens)

    def serialize(self, debug=False, color=False):
        # return ' '.join(str(token) for token in self.tokens)

        def token_serialize(t: Token) -> str:
            if debug:
                return t.debug_str()
            elif color:
                return t.color_str()
            else:
                return str(t)

        assignments = {
            choice.ident: choice.choices
                for choice in set(
                    choice for choice in self if isinstance(choice, ChoiceSpecialToken)
                )
        }

        combinations = list(product(*assignments.values()))

        command_choices: List[str] = []
        for combination in combinations:
            command_choice = []
            for token in self:
                if isinstance(token, ChoiceSpecialToken):
                    index = list(assignments.keys()).index(token.ident)
                    command_choice += [token_serialize(token) for token in combination[index]]
                else:
                    command_choice.append(token_serialize(token))
            command_choices.append(TOKEN_SEP.join(command_choice))

        return COMMAND_SEP.join(command_choices)
    
    def __str__(self):
        return self.serialize()

class TokensRef:
    def get_cmds(self) -> List[TokensContainer | Self]:
        return []
    
    def single_line_tokenize(self) -> List[Token]:
        cmds = self.resolve()
        assert len(cmds) == 1
        return cmds[0].tokenize()

    def tokenize(self) -> List[Token]:
        tokens = []
        for cmd in self.resolve():
            tokens += cmd.tokens
            tokens.append(CommandSepToken())
        return tokens[:-1]  # remove trailing CommandSepToken()
    
    def serialize(self, **kwargs):
        return COMMAND_SEP.join(
            TokensContainer(*tokens).serialize(**kwargs) for tokens in self.resolve()
        )
    
    def __str__(self):
        return self.serialize()
    
    def resolve(self) -> List[TokensContainer]:
        return [(cmd.resolve() if isinstance(cmd, TokensRef) else cmd) for cmd in self.get_cmds()]

class Program:
    def __init__(self, *cmds: TokensContainer | TokensRef):
        self.cmds: List[TokensContainer | TokensRef] = list(cmds)

    def __len__(self):
        return len(self.cmds)

    def __iter__(self):
        return self.cmds.__iter__()
    
    # def __getitem__(self, idx):
    #     return self.cmds[idx]
    
    def __setitem__(self, idx, newval: TokensContainer | TokensRef):
        self.cmds[idx] = newval
    
    def serialize(self, **kwargs):
        return COMMAND_SEP.join(cmd.serialize(**kwargs) for cmd in self if cmd is not None)
    
    def __str__(self):
        return self.serialize()
    
    def append(self, cmd: TokensContainer | TokensRef):
        self.cmds.append(cmd)

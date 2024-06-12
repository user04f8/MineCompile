from typing import Tuple, List, Self
from uuid import uuid4
from itertools import product
from enum import StrEnum

from termcolor import colored
from .debug_utils import *

_Color = Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "light_grey",
    "dark_grey", "light_red", "light_green", "light_yellow", "light_blue", "light_magenta", "light_cyan", "white",
]
class _Colors:
    # termcolor colors for each token type
    DEFAULT = 'white'
    RAW = 'light_green' # hardcoded to be on_color='on_black'
    COMMAND = 'light_magenta' # hardcoded to be bold
    SUBCOMMAND = 'light_magenta'
    FUNCTION = 'light_cyan' # hardcoded to be underlined
    STR = 'green'

    SERIALIZABLE: Dict[str, _Color] = {
        'Selector': 'cyan',
        'ResourceLocation': 'blue'
    }


class Token:
    def __str__(self) -> str:
        raise NotImplementedError

    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), _Colors.DEFAULT)
    
    def debug_str(self) -> str:
        return self.color_str()
    
    def __format__(self, format_spec: str) -> str:
        return str(self)
    
class Serializable(Token):
    def __init__(self):
        self.token: Token
    
    def __str__(self):
        return self.token.__str__()
    
    def color_str(self) -> str:
        return colored(self.__str__(), _Colors.SERIALIZABLE.get(self.__class__.__name__, _Colors.DEFAULT))

class RawToken(Token):
    def __init__(self, s: str):
        self.s = s
    
    def __str__(self):
        return self.s

    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), _Colors.RAW, on_color='on_black')
    
class JoinToken(Token):
    def __init__(self, *tokens: Token | str):
        self.tokens = [token if isinstance(token, Token) else RawToken(token) for token in tokens]

    def __str__(self):
        return ''.join(str(t) for t in self.tokens)
    
    def color_str(self) -> str:
        return ''.join(t.color_str() for t in self.tokens)


class StrToken(Token):
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s
    
    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), _Colors.STR)

class CommandNameToken(RawToken):
    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), _Colors.COMMAND, attrs=["bold"])

class CommandKeywordToken(RawToken):
    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), _Colors.SUBCOMMAND)

def serialize_function_name(namespace, path, color=False):
    s = f'{namespace}:{'/'.join(path)}'
    if color:
        # noinspection PyTypeChecker
        return colored(s, _Colors.FUNCTION, attrs=["underline"])
    
    return s

class FunctionToken(Token):
    def __init__(self, namespace: str, path: List[str]):
        self.namespace = namespace
        self.path = path

    def __str__(self):
        return f'function {serialize_function_name(self.namespace, self.path)}'
    
    def color_str(self):
        # noinspection PyTypeChecker
        return colored('function', _Colors.COMMAND, attrs=["bold"]) + ' ' + colored(serialize_function_name(self.namespace, self.path), _Colors.FUNCTION, attrs=["underline"])

class TokenError(Exception):
    pass

class ParseErrorToken(Token):
    def __init__(self, err: str):
        print_err(f'parse error {err}')
        self.err = err

    def __str__(self):
        raise TokenError(self.err)
    
    def debug_str(self):
        return colored(f'$ParseError:{self.err}$', 'red', attrs=['bold'])

class SerializeErrorToken(Token):
    def __init__(self, err):
        print_err(f'serialize error {err}')
        self.err = err

    def __str__(self):
        raise TokenError(self.err)
    
    def debug_str(self):
        return colored(f'$SerializeError:{self.err}$', 'red', attrs=['bold'])

TOKEN_SEP = ' '
REMOVE_TOKEN_SEP = '$remove_token_sep'
COMMAND_SEP = '\n'

class CommandSepToken(Token):
    def __str__(self):
        return COMMAND_SEP + REMOVE_TOKEN_SEP
    
    def debug_str(self) -> str:
        return colored('¦', 'grey') + COMMAND_SEP + REMOVE_TOKEN_SEP

class Choice(Token):
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

    def __hash__(self):
        if self.ident is None:
            return self.uuid.int
        else:
            return hash(self.ident)

class ArgToken(Token):
    def __init__(self, ident: int):
        self.ident = ident

    def __str__(self):
        return f'$TODO $arg:{self.ident}'  # TODO

class Flag:
    def __init__(self, name=None, resource_loc='_internal:flags'):
        if name is None:
            name = uuid4().hex
        self.name = name
        self.resource_loc = resource_loc

    def serialize(self):
        return f'storage {self.resource_loc} {self.name}'

class ResetFlagToken(Token):
    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data remove {self.flag.serialize()}'

class SetFlagToken(Token):
    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data modify {self.flag.serialize()} set value 1'
    
class CheckFlagToken(Token):
    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data {self.flag.serialize()}'
    


class SelectorToken(Token):
    def __init__(self, s: str = 's', **kwargs):
        # TODO structure kwargs by https://minecraft.wiki/w/Target_selectors
        assert s in {'p', 'r', 'a', 'e', 's', 'n'}
        self.s = s
        self.kwargs = kwargs

    def __str__(self):
        if self.kwargs == {}:
            return f'@{self.s}'
        else:
            return f'@{self.s}[{",".join(f"{key}={val}" for key, val in self.kwargs.items())}]'

class TokensContainer:
    def __init__(self, *tokens: Token):
        assert all(isinstance(token, Token) for token in tokens), f"{[type(token) for token in tokens]}"
        self.tokens = tokens

    def __iter__(self):
        return self.tokens.__iter__()
    
    def tokenize(self):
        return list(self.tokens)

    def serialize(self, debug=False, color=False, force_color=None) -> str | SerializeErrorToken:
        def token_serialize(t: Token) -> str:
            if force_color:
                return colored(str(t), force_color)
            elif debug:
                return t.debug_str()
            elif color:
                return t.color_str()
            else:
                return str(t)

        try:
            assignments = {
                choice.ident: choice.choices
                    for choice in set(
                        choice for choice in self if isinstance(choice, Choice)
                    )
            }

            combinations = list(product(*assignments.values()))

            command_choices: List[str] = []
            for combination in combinations:
                command_choice = []
                for token in self:
                    if isinstance(token, Choice):
                        index = list(assignments.keys()).index(token.ident)
                        command_choice += [token_serialize(token) for token in combination[index]]
                    else:
                        command_choice.append(token_serialize(token))
                command_choices.append(('  ' if debug and len(combinations) > 1 else '') + TOKEN_SEP.join(command_choice))
            if debug:
                return colored(' |\n', 'grey').join(command_choices)
            else:
                return COMMAND_SEP.join(command_choices)
        except Exception as e:
            return SerializeErrorToken(e)
             
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
    
    def serialize(self, debug=False, **kwargs) -> str | SerializeErrorToken:
        if debug:
            sep = colored(' |\n', 'grey')
        else:
            sep = COMMAND_SEP
        try:
            return sep.join(
                tokens.serialize(debug=debug, **kwargs) for tokens in self.resolve()
            )
        except Exception as err:
            return SerializeErrorToken(err)
    
    def __str__(self):
        return self.serialize()

    def resolve(self) -> List[TokensContainer]:
        resolved_cmds = [resolved_cmd for cmd in self.get_cmds() for resolved_cmd in (cmd.resolve() if isinstance(cmd, TokensRef) else [cmd]) ]
        return resolved_cmds

class Program:
    def __init__(self, *cmds: TokensContainer | TokensRef):
        self.cmds: List[TokensContainer | TokensRef] = list(cmds)
        self.removed = False

    def __len__(self):
        return len(self.cmds)

    def __iter__(self):
        return self.cmds.__iter__()
    
    # def __getitem__(self, idx):
    #     return self.cmds[idx]
    
    def __setitem__(self, idx, new_val: TokensContainer | TokensRef):
        self.cmds[idx] = new_val

    def remove(self):
        self.removed = True
    
    def append(self, cmd: TokensContainer | TokensRef):
        self.cmds.append(cmd)

    def serialize(self, debug=False, **kwargs):
        if debug:
            sep = colored(' ||\n', 'grey')
        else:
            sep = COMMAND_SEP
        return ('# UNUSED\n' if self.removed else '') + sep.join(s for s in (cmd.serialize(debug=debug, **kwargs) for cmd in self if cmd is not None) if s is not '')

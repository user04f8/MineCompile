from typing import Literal, Self, List, Dict
from uuid import uuid4
from itertools import product

from termcolor import colored

from langcraft.json_utils import JSON

from .debug_utils import *

_Color = Literal["black", "grey", "red", "green", "yellow", "blue", "magenta", "cyan", "light_grey",
    "dark_grey", "light_red", "light_green", "light_yellow", "light_blue", "light_magenta", "light_cyan", "white",
]
class _Colors:
    # termcolor colors for each token type
    DEFAULT = 'white'
    SERIALIZABLE_DEFAULT = 'red'
    RAW = 'red' # hardcoded to be on_color='on_black'
    COMMAND = 'light_magenta' # hardcoded to be bold
    SUBCOMMAND = 'light_magenta'
    FUNCTION = 'light_cyan' # hardcoded to be underlined
    STR = 'green'
    MISC = 'light_grey'
    FLAG = 'dark_grey'

    SERIALIZABLE: Dict[str, _Color] = {
        'ResourceLocation': 'blue',
        '_SelectorBase': 'white',
        '_SingleSelectorBase': 'white',
        'Entities': 'green',
        'Self': 'white',
        'Pos': 'yellow',
        'Rot': 'yellow'
    }


class Token:
    COLOR = _Colors.DEFAULT

    def __str__(self) -> str:
        raise NotImplementedError

    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), self.COLOR)
    
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
        # return self.color_str()
        return colored(self.__str__(), _Colors.SERIALIZABLE.get(self.__class__.__name__, _Colors.SERIALIZABLE_DEFAULT))

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
    COLOR = _Colors.STR
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return self.s

class MiscToken(StrToken):
    COLOR = _Colors.MISC

class CommandNameToken(StrToken):
    COLOR = _Colors.COMMAND

    def color_str(self) -> str:
        # noinspection PyTypeChecker
        return colored(self.__str__(), self.COLOR, attrs=['bold'])

class CommandKeywordToken(StrToken):
    COLOR = _Colors.SUBCOMMAND

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
        raise err
        self.err = err

    def __str__(self):
        return str(self.err)
    
    def debug_str(self):
        return colored(f'$ParseError:{self.err}$', _Colors.ERR, attrs=['bold'])

class SerializeErrorToken(Token):
    def __init__(self, err):
        print_err(f'serialize error {err}')
        raise err
        self.err = err

    def __str__(self):
        return str(self.err)
    
    def debug_str(self):
        return colored(f'$SerializeError:{self.err}$', _Colors.ERR, attrs=['bold'])

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
    COLOR = _Colors.FLAG

    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data remove {self.flag.serialize()}'

class SetFlagToken(Token):
    COLOR = _Colors.FLAG

    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data modify {self.flag.serialize()} set value 1'
    
class CheckFlagToken(Token):
    COLOR = _Colors.FLAG

    def __init__(self, flag: Flag):
        self.flag = flag

    def __str__(self):
        return f'data {self.flag.serialize()}'
    
class SelectorToken(Token):
    def __init__(self, s: str = 's', **kwargs):
        # TODO structure kwargs by https://minecraft.wiki/w/Target_selectors
        self.s = s
        self.kwargs = kwargs

    def __str__(self):
        if self.kwargs == {}:
            return f'@{self.s}'
        else:
            return f'@{self.s}[{",".join(f"{key}={val}" for key, val in self.kwargs.items())}]'

class ResourceLocToken(Token):
    def __init__(self, namespace: str = 'minecraft', path: List[str] = []):
        # TODO structure kwargs by https://minecraft.wiki/w/Target_selectors
        self.namespace = namespace
        self.path = path

    def __str__(self):
        return self.namespace + ':' + '/'.join(p for p in self.path)
    
class JSONRefToken(ResourceLocToken):
    pass

class TokensContainer:
    def __init__(self, *tokens: Token):
        assert all(isinstance(token, Token) for token in tokens), f"{[type(token) for token in tokens]}"
        self._tokens = list(tokens)

    @property
    def tokens(self):
        return self._tokens

    def __iter__(self):
        return self.tokens.__iter__()
    
    def tokenize(self):
        return list(self.tokens)

    def serialize(self, debug=False, color=False, force_color=None, validate_fun=lambda namespace, path: True, validate_json=lambda namespace, path: True) -> str | SerializeErrorToken:
        def token_serialize(t: Token) -> str:
            if isinstance(t, FunctionToken):
                if not validate_fun(t.namespace, t.path):
                    return colored(str(t), 'red', 'on_black', attrs=['blink', 'bold'])
            if isinstance(t, JSONRefToken):
                if not validate_json(t.namespace, t.path):
                    return colored(str(t), 'red', 'on_black', attrs=['blink', 'bold'])

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
    
    def single_line_tokenize(self) -> List[Token] | None:
        cmds = self.resolve()
        if len(cmds) > 1:
            return None
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
        resolved_cmds = [resolved_cmd for cmd in self.get_cmds() for resolved_cmd in (cmd.resolve() if isinstance(cmd, TokensRef) else [cmd])]
        return resolved_cmds

class Program:
    def __init__(self, *cmds: TokensContainer | TokensRef):
        self.cmds: List[TokensContainer | TokensRef] = list(cmds)
        self.unused = False

    def __len__(self):
        return len(self.cmds)

    def __iter__(self):
        return self.cmds.__iter__()
    
    def __getitem__(self, idx):
        return self.cmds[idx]
    
    def __setitem__(self, idx, new_val: TokensContainer | TokensRef):
        self.cmds[idx] = new_val

    def mark_unused(self):
        self.unused = True
    
    def append(self, cmd: TokensContainer | TokensRef):
        self.cmds.append(cmd)

    def unwrap_to(self, i: int, cmds: List[TokensContainer | TokensRef]):
        """
        Removes self.cmds[i] and inserts cmds at index i
        """
        self.cmds = self.cmds[:i] + cmds + self.cmds[i+1:]

    def optimize(self):
        i = 0
        while i < len(self.cmds) - 1:
            cmd0, cmd1 = self.cmds[i], self.cmds[i+1]
            try:
                if hasattr(cmd0, 'join_with_cmd'):
                    cmd01 = cmd0.join_with_cmd(cmd1)
                elif hasattr(cmd1, 'right_join_with_cmd'):
                    cmd01 = cmd1.right_join_with_cmd(cmd0)
                else:
                    cmd01 = None
                if cmd01:
                    print_debug(f'joined cmds: {cmd0} || {cmd1} --> {cmd01}')
                    self.cmds[i] = cmd01
                    del self.cmds[i+1]
                    i -= 1
            except TypeError as e:
                print_warn(f'invalid types for optim: {e}')
            i += 1

    def serialize(self, debug=False, **kwargs):
        if debug:
            sep = colored(' ||\n', 'grey')
        else:
            sep = COMMAND_SEP
        return ('# UNUSED\n' if self.unused else '') + sep.join(
                    s for s in (
                        cmd.serialize(debug=debug, **kwargs) for cmd in self if cmd is not None
                    ) if s != ''
                )

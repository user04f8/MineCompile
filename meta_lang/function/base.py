from copy import deepcopy
from enum import Enum
from typing import Any, List, Optional, Dict, Self
from .serialize import *
from uuid import uuid4
from pathlib import Path

DATAPACK_ROOT: str = '%DATAPACK_ROOT%'

class Globals:
    def __init__(self, namespace='main'):
        self.namespace: str = namespace
        self.path: List[str] = []
        self.cmds: Dict[str, List[Command | CommandRef]] = {self.get_full_path(): []}
    
    def get_full_path(self):
        return '/'.join([DATAPACK_ROOT, self.namespace, 'function'] + self.path)

    def add_current_path(self):
        if self.get_full_path() not in self.cmds:
            self.cmds[self.get_full_path()] = []
        
    def add_cmd(self, cmd):
        idx = len(self.cmds[self.get_full_path()])
        self.cmds[self.get_full_path()].append(cmd)
        return (self.get_full_path(), idx)

    def clear_cmd(self, pathed_idx):
        full_path, idx = pathed_idx
        self.cmds[full_path][idx] = None

    def set_cmd(self, pathed_idx, cmd):
        full_path, idx = pathed_idx
        self.cmds[full_path][idx] = cmd

GLOBALS = Globals()

class RelativeNamespace:
    def __init__(self, name: str):
        self.name = name
        self.old_name = GLOBALS.namespace

    def __enter__(self):
        GLOBALS.namespace = self.name
        GLOBALS.add_current_path()

    def __exit__(self, *args):
        GLOBALS.namespace = self.old_name

class Pathspace:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        GLOBALS.path.append(self.name)
        GLOBALS.add_current_path()

    def __exit__(self, *args):
        GLOBALS.path.pop()

class Namespace:
    def __init__(self, namespace: str, full_path: List[str]):
        self.old_namespace = GLOBALS.namespace
        self.new_namespace = namespace
        self.old_path = GLOBALS.path
        self.new_path = full_path

    def __enter__(self):
        GLOBALS.namespace = self.new_namespace
        GLOBALS.path = self.new_path
        GLOBALS.add_current_path()

    def __exit__(self, *args):
        GLOBALS.path = self.old_path
        GLOBALS.namespace = self.old_namespace

class Statement(CommandRef):
    def __init__(self, cmds: str | List[Command], add=True):
        if isinstance(cmds, str):
            cmds = [Command(*(StrToken(token) for token in cmd.split()), CommandSepToken()) for cmd in cmds.split('\n')]
        self.cmds = cmds

        if add:
            self.idx = GLOBALS.add_cmd(self)

    def get_cmds(self) -> List[Command]:
        return self.cmds
    
    def tokenize(self) -> List[Token]:
        return [token for cmd in self.get_cmds() for token in cmd.tokens]
    
    def clear(self):
        GLOBALS.clear_cmd(self.idx)

class DummyStatement(Statement):
    def __init__(self):
        pass

    def get_cmds(self) -> List[Command]:
        return []
    
    def tokenize(self) -> List[Token]:
        return []
    
    def clear(self):
        pass

class ConditionType(Enum):
    FALSE = 0
    TRUE = 1
    STR = 3
    ALL = 10
    ANY = 11

class Condition:
    SIMPLE = {ConditionType.STR, }

    def __init__(self, value: str | List['Condition'] = '', condition_type: ConditionType = ConditionType.STR):
        self.condition_type = condition_type
        self.value = value
        self.inverted = False

    @property
    def always_true(self):
        return self.condition_type == ConditionType.TRUE
    
    @property
    def always_false(self):
        return self.condition_type == ConditionType.FALSE
    
    def __invert__(self) -> 'Condition':
        if self.always_true:
            self.condition_type = ConditionType.FALSE
        elif self.always_false:
            self.condition_type = ConditionType.TRUE
        elif self.condition_type in {ConditionType.ANY, ConditionType.ALL}:
            self.value = [~sub_condition for sub_condition in self.value]  # De Morgan's laws
        else:
            self.inverted = not self.inverted

    def __and__(self, c: 'Condition') -> 'Condition':
        if self.always_false or c.always_true:
            return self
        elif self.always_true or c.always_false:
            return c
        if self.condition_type == ConditionType.ALL:
            if c.condition_type == ConditionType.ALL:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        return Condition(condition_type=ConditionType.ALL, value=[self, c])

    def __or__(self, c: 'Condition') -> 'Condition':
        if self.always_false or c.always_true:
            return c
        elif self.always_true or c.always_false:
            return self
        if self.condition_type == ConditionType.ANY:
            if c.condition_type == ConditionType.ANY:
                for v in c.value:
                    self.value.append(v)
            else:
                self.value.append(c)
            return self
        return Condition(condition_type=ConditionType.ANY, value=[self, c])

    def tokenize(self) -> List[Token]:
        match self.condition_type:
            case ConditionType.STR:
                return [(Keyword.UNLESS if self.inverted else Keyword.IF), StrToken(self.value)]
            case ConditionType.ALL:
                if all(condition.condition_type in self.SIMPLE for condition in self.value):
                    return [token for condition in self.value for token in condition.tokenize()]
                else:
                    tokens = []
                    for i, condition in enumerate(self.value):
                        if condition.condition_type not in self.SIMPLE:
                            break
                        tokens += condition.tokenize()
                    rem_conditions = self.value[i:]
                    tokens += Fun.wrap_tokens([Keyword.EXECUTE] + [token for condition in rem_conditions for token in condition.tokenize()])
                    return tokens
            case ConditionType.ANY:
                return [Choice(choices=tuple(str(c) for c in self.value))]

class Block(Statement):
    def __init__(self, *statements: Statement | str):
        self.statements = tuple((Statement(statement) if isinstance(statement, str) else statement) for statement in statements)

    def get_cmds(self) -> List[Command]:
        return [cmd for statement in self.statements for cmd in statement.get_cmds()]
    
    def __len__(self):
        return len(self.statements)
    
    def clear(self):
        for statement in self.statements:
            statement.clear()

class ArgType(Enum):
    INT = 0
    
    # TUPLE = 10

    UNKOWN = -1

    @staticmethod
    def from_type(t):
        return {
            int: ArgType.INT,
        }.get(t, ArgType.UNKOWN)

    @staticmethod
    def infer(x):
        match x:
            # case tuple(xs) | list(xs):
            #     self.type = SimpleValType.TUPLE
            #     self.types = tuple(ValType(x) for x in xs)
            case int(x):
                return ArgType.INT
            case _:
                return ArgType.UNKOWN
            
    def cast(self, x):
        match self:
            case _:
                return x
            
class Value:
    def __init__(self, x, type: Optional[ArgType]):
        if type is None:
            self.type = ArgType.infer(x)
        else:
            x = type.cast(x)
            self.type = type
        self.x = x

# class ArgsType(ValType):
#     def __init__(self, *types: type):
#         self.type = SimpleValType.TUPLE
#         self.types = tuple(ValType(type) for type in types)

#     def __call__(self, x) -> Value:
#         return []


class Alias(DummyStatement):
    def __init__(self, kw, kw_replace):
        self.kw: Token = kw
        self.kw_replace: Token = kw_replace

    def tokenize(self) -> List[Token]:
        return []

    def apply_token(self, token: Token):
        if self.kw == token:
            return self.kw_replace

    def apply(self, cmd: Command):
        return Command(*(self.apply_token(token) for token in cmd.tokens))
        
class ArgNames(Alias):
    def __init__(self, *args):
        self.args = args
        self.kw = self.default()

    @staticmethod
    def default(i):
        return VarToken(SelfSelector, f'_{i}')

class FunStatement(Statement):
    def __init__(self, fun: 'Fun'):
        self.fun = fun
        self.cmds = [Command(FunctionToken(self.fun.namespace, self.fun.path))]
        self.idx = None

    def clear(self):
        pass

    def __call__(self, *args):
        vals = (Value(val, type=in_type) for in_type, val in zip(self.fun.in_types, args))
        
        if isinstance(self.fun.block.statements[0], ArgNames):
            funct_arg_names = self.fun.block.statements[0]
            self.fun.block.statements = self.fun.block.statements[1:]
            assignments = {funct_arg_name: val for funct_arg_name, val in zip(funct_arg_names, vals)}
        else:
            assignments = {ArgNames.default(i): arg for i, arg in enumerate(args)}
        
        for statement in self.fun.block.statements:
            pass


class Fun:
    def __init__(self, name: Optional[str] = None, namespace: Optional[str] = None, path: Optional[List[str]] = None):
        self.block = None

        if namespace is None:
            self.namespace = GLOBALS.namespace
        else:
            self.namespace = namespace
        
        self.uuid = uuid4()
        if name is None:
            self.name = str(self.uuid)
        else:
            self.name = name

        self.out_types = self.in_types = ()
        
        self.refs = []
        self.idxes = []
        
        if path is None:
            self.path = GLOBALS.path + [self.name]
        else:
            self.path = path

    def __class_getitem__(self, *types):
        self.out_type = tuple(ArgType(t) for t in types)

    def __getitem__(self, *types):
        self.in_types = tuple(ArgType(t) for t in types)
       
    def __call__(self, *statements: Statement) -> FunStatement:
        if self.block is None:
            self.block = Block(*statements)
            self.block.clear()

            with Namespace(self.namespace, self.path):
                for statement in self.block.statements:
                    for cmd in statement.get_cmds():
                        self.idxes.append(GLOBALS.add_cmd(cmd))

            return FunStatement(self)  
        else:
            raise ValueError('Function block already assigned')
    
    @staticmethod
    def wrap_tokens(tokens: List[Token]) -> List[Token]:
        uuid = uuid4()
        namespace = GLOBALS.namespace
        with Pathspace(str(uuid)):
            GLOBALS.add_cmd(Command(*tokens))
            path = GLOBALS.path
        return FunctionToken(namespace, path)
    
# def resolve_refs() -> List[Command]:
#     cmds = deepcopy(GLOBALS.cmds)
#     for _, file_cmds in cmds.items():
#         [(cmd.resolve() if isinstance(cmd, CommandRef) else cmd) for cmd in file_cmds if cmd is not None]
#     return cmds

def compile_file(file_cmds: List[Command | CommandRef]):
    # ''.join(str(cmd) for cmd in file_cmds if cmd is not None)
    for cmd in file_cmds:
        pass

def compile(cmds: Dict[str, List[Command | CommandRef]] = GLOBALS.cmds, root_dir: str = './datapacks/testing/data') -> Dict[str, str]:
    out = {}
    for file_path, file_cmds in cmds.items():
        if any(file_cmd is not None for file_cmd in file_cmds):
            file_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction\n'
            out[file_path] = compile_file(file_cmds)
    return out

def display_all_cmds(cmds: Dict[str, List[Command | CommandRef]] = GLOBALS.cmds, root_dir: str = './datapacks/testing/data'):
    out = ''
    for file_path, file_cmds in cmds.items():
        if any(file_cmd is not None for file_cmd in file_cmds):
            out += file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction\n'
            out += ''.join(str(cmd) for cmd in file_cmds if cmd is not None)
            out += '\n'
    print(out)

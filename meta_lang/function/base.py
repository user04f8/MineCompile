from enum import Enum
from typing import List, Optional, Dict
from .serialize import Command, Program, Token, StrToken, FunctionToken, Choice, Keyword
from uuid import uuid4

DATAPACK_ROOT: str = './datapacks/testing/data'
CURRENT_NAMESPACE: str = 'main'
CURRENT_PATH: List[str] = []
def get_full_path():
    return '/'.join([DATAPACK_ROOT, CURRENT_NAMESPACE, 'function'] + CURRENT_PATH)
GLOBAL_CMDS: Dict[str, Program] = {get_full_path(): []}

class Namespace:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        CURRENT_PATH.append(self.name)
        GLOBAL_CMDS[get_full_path()] = []

    def __exit__(self, *args):
        CURRENT_PATH.pop()

class GlobalNamespace:
    def __init__(self, namespace: str, full_path: List[str]):
        self.old_namespace = CURRENT_NAMESPACE
        self.new_namespace = namespace
        self.old_path = CURRENT_PATH
        self.new_path = full_path

    def __enter__(self):
        global CURRENT_PATH, CURRENT_NAMESPACE
        CURRENT_NAMESPACE = self.new_namespace
        CURRENT_PATH = self.new_path
        GLOBAL_CMDS[get_full_path()] = []

    def __exit__(self, *args):
        global CURRENT_PATH, CURRENT_NAMESPACE
        CURRENT_PATH = self.old_path
        CURRENT_NAMESPACE = self.old_namespace

def add_cmd(cmd):
    idx = len(GLOBAL_CMDS[get_full_path()])
    GLOBAL_CMDS[get_full_path()].append(cmd)
    return (CURRENT_PATH, idx)

def clear_cmd(pathed_idx):
    path, idx = pathed_idx
    GLOBAL_CMDS[get_full_path()][idx] = None

def set_cmd(pathed_idx, cmd):
    path, idx = pathed_idx
    GLOBAL_CMDS[get_full_path()][idx] = cmd

class Statement:
    def __init__(self, cmd: str | Command):
        if isinstance(cmd, str):
            cmd = Command([StrToken(cmd)])
        self.cmd = cmd

        self.idx = add_cmd(self.cmd)

    def get_cmds(self) -> List[Command]:
        return [self.cmd]
    
    def tokenize(self) -> List[Token]:
        return [token for cmd in self.get_cmds() for token in cmd.tokens]
    
    def undo(self):
        clear_cmd(self.idx)

class ConditionType(Enum):
    STR = 0
    ALL = 10
    ANY = 11

class Condition:
    SIMPLE = {ConditionType.STR, }

    def __init__(self, value: str | List['Condition'], condition_type: ConditionType = ConditionType.STR):
        self.condition_type = condition_type
        self.value = value
        self.inverted = False
    
    def __invert__(self) -> 'Condition':
        self.inverted = not self.inverted

    def __and__(self, c: 'Condition') -> 'Condition':
        if self.always_falsy() or c.always_truthy():
            return self
        elif self.always_truthy() or c.always_falsy():
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
        if self.always_falsy() or c.always_truthy():
            return c
        elif self.always_truthy() or c.always_falsy():
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
                        if condition not in self.SIMPLE:
                            break
                        tokens += condition.tokenize()
                    rem_conditions = self.value[i:]
                    tokens += Function.wrap_tokens([Keyword.EXECUTE] + [token for condition in rem_conditions for token in condition.tokenize()])
                    return tokens
            case ConditionType.ANY:
                return [Choice(choices=tuple(str(c) for c in self.value))]

    def always_truthy(self):
        return False
    
    def always_falsy(self):
        return False
    
    def sanity_check(self):
        assert not(self.always_truthy() and self.always_falsy())
    
class Function:
    def __init__(self, *statements: Statement, namespace: str = CURRENT_NAMESPACE, path: Optional[List[str]] = None):
        self.statements = statements
        for statement in self.statements:
            statement.undo()
        self.namespace = namespace
        self.uuid = uuid4()
        self.idxes = []
        
        if path is None:
            self.path = CURRENT_PATH + [str(self.uuid)]
        else:
            self.path = path
        
        with GlobalNamespace(self.namespace, self.path):
            for statement in self.statements:
                for cmd in statement.get_cmds():
                    self.idxes.append(add_cmd(cmd))

    def get_token(self) -> Token:
        return FunctionToken(self.namespace, self.path)
    
    @staticmethod
    def wrap_tokens(tokens: List[Token]) -> List[Token]:
        uuid = uuid4()
        namespace = CURRENT_NAMESPACE
        with Namespace(str(uuid)):
            add_cmd(Command(tokens=tokens))
            path = CURRENT_PATH
        return FunctionToken(namespace, path)
    
def display_all_cmds(root_dir: str = './datapacks/testing/data/'):
    global DATAPACK_ROOT
    DATAPACK_ROOT = root_dir
    out = ''
    for file_path, file_cmds in GLOBAL_CMDS.items():
        if any(file_cmd is not None for file_cmd in file_cmds):
            out += file_path
            out += '.mcfunction\n'
            out += '\n'.join(str(cmd) for cmd in file_cmds if cmd is not None)
            out += '\n'
    print(out)
    return out
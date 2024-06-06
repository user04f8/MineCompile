from copy import deepcopy
from enum import Enum
from typing import Any, List, Optional, Dict, Self
from .serialize import *
from .types import *
from uuid import uuid4
from pathlib import Path

DATAPACK_ROOT: str = '%DATAPACK_ROOT%'

class Globals:
    def __init__(self, namespace='main'):
        self.namespace: str = namespace
        self.path: List[str] = []
        self.programs: Dict[str, Program] = {self.get_full_path(): Program()}
    
    def get_full_path(self):
        return '/'.join([DATAPACK_ROOT, self.namespace, 'function'] + self.path)

    def add_current_path(self):
        if self.get_full_path() not in self.programs:
            self.programs[self.get_full_path()] = Program()
        
    def add_cmd(self, cmd):
        idx = len(self.programs[self.get_full_path()])
        self.programs[self.get_full_path()].append(cmd)
        return (self.get_full_path(), idx)

    def clear_cmd(self, pathed_idx):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = None

    def set_cmd(self, pathed_idx, cmd):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = cmd

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

class Statement(TokensRef):
    def __init__(self, cmds: str | List[TokensContainer], add=True):
        if isinstance(cmds, str):
            self.cmds = [TokensContainer(*(StrToken(token) for token in cmd.split())) for cmd in cmds.split('\n')]
        elif isinstance(cmds, List):
            self.cmds = cmds
        else:
            raise TypeError(f"Invalid type for Statement cmds {type(cmds)}")

        if add:
            self.idx = GLOBALS.add_cmd(self)
        else:
            self.idx = None

    def get_cmds(self) -> List[TokensContainer]:
        return self.cmds
    
    def clear(self):
        if self.idx is not None:
            GLOBALS.clear_cmd(self.idx)

class EmptyStatement(TokensRef):
    def __init__(self):
        pass

    def get_cmds(self) -> List[TokensContainer]:
        return []
    
    def tokenize(self) -> List[Token]:
        return []
    
    def clear(self):
        pass

class Block(Statement):
    def __init__(self, *statements: Statement | str):
        self.statements = tuple((Statement(statement) if isinstance(statement, str) else statement) for statement in statements)

    def get_cmds(self) -> List[TokensContainer]:
        return [cmd for statement in self.statements for cmd in statement.get_cmds()]
    
    def __len__(self):
        return len(self.statements)
    
    def clear(self):
        for statement in self.statements:
            statement.clear()

class ArgType(Enum):
    NONE = 0
    INT = 1
    
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
            case None:
                return ArgType.NONE
            case _:
                return ArgType.UNKOWN
    
    def cast(self, x):
        match self:
            case ArgType.INT:
                return Int32(x)
            case _:
                raise TypeError(f"Type {self} doesn't support input {x}")
            
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


class Alias(EmptyStatement):
    def __init__(self, kw, kw_replace):
        self.kw: Token = kw
        self.kw_replace: Token = kw_replace

    def tokenize(self) -> List[Token]:
        return []

    def apply_token(self, token: Token):
        if self.kw == token:
            return self.kw_replace

    def apply(self, cmd: TokensContainer):
        return TokensContainer(*(self.apply_token(token) for token in cmd))
        
class ArgNames(Alias):
    def __init__(self, *args):
        self.args = args
        self.kw = self.default()

    @staticmethod
    def default(i):
        return VarToken(Selector(), f'_{i}')

class FunStatement(Statement):
    def __init__(self, fun: 'Fun'):
        self.fun = fun
        self.cmds = [TokensContainer(FunctionToken(self.fun.namespace, self.fun.path))]
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
        self.out_type = tuple(ArgType.from_type(t) for t in types)
        return self

    def __getitem__(self, *types):
        self.in_types = tuple(ArgType.from_type(t) for t in types)
        return self
       
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
            GLOBALS.add_cmd(TokensContainer(*tokens))
            path = GLOBALS.path
        return FunctionToken(namespace, path)
    
# def resolve_refs() -> List[Command]:
#     cmds = deepcopy(GLOBALS.cmds)
#     for _, file_cmds in cmds.items():
#         [(cmd.resolve() if isinstance(cmd, CommandRef) else cmd) for cmd in file_cmds if cmd is not None]
#     return cmds

def compile_program(program: Program, **serialize_kwargs):
    for cmd in program:
        pass  # TODO run any final compilation postprocessing
    
    return program.serialize(**serialize_kwargs)

def compile_all(programs: Dict[str, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', write=False, color=False, debug=False) -> Dict[str, str]:
    out_files: Dict[Path, str] = {}
    for file_path, program in programs.items():
        if any(file_cmd is not None for file_cmd in program):
            file_path = Path(file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction\n')
            out_files[file_path] = compile_program(program, color=color, debug=debug)
            if write:
                file_path.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(out_files[file_path])
    return out_files

# def display_all(programs: Dict[str, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data'):
    # out = ''
    # for file_path, file_cmds in cmds.items():
    #     if any(file_cmd is not None for file_cmd in file_cmds):
    #         out += file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction\n'
    #         out += ''.join(str(cmd) for cmd in file_cmds if cmd is not None)
    #         out += '\n'
    # compiled = compile(programs, root_dir)
    # for file_path, serialized_file in compiled.items():
    #     print(file_path)
    #     print(serialized_file)

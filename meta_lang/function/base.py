from copy import copy
from enum import Enum
from typing import List, Optional, Dict
from uuid import uuid4
from pathlib import Path

from .globals import GLOBALS, DATAPACK_ROOT
from .serialize import *
from .types import *
from .debug_utils import *


class Namespace:
    def __init__(self, name: str, full_path: Optional[List[str]] = None):
        self.old_name = GLOBALS.namespace
        self.name = name
        self.old_path = GLOBALS.path
        self.new_path = full_path

    def __enter__(self):
        GLOBALS.set_namespace(self.name, self.new_path)

    def __exit__(self, *args):
        GLOBALS.set_namespace(self.old_name, self.old_path)

class Pathspace:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        GLOBALS.enter_path(self.name)

    def __exit__(self, *args):
        GLOBALS.exit_path(self.name)

class Statement(TokensRef):
    def __init__(self, cmds: str | Token | TokensContainer | List[Token] | List[TokensContainer], add=True):
        if isinstance(cmds, str):
            self.cmds = [TokensContainer(*(StrToken(token) for token in cmd.split())) for cmd in cmds.split('\n')]
        elif isinstance(cmds, Token):
            self.cmds = [TokensContainer(cmds)]
        elif isinstance(cmds, TokensContainer):
            self.cmds = [cmds]
        elif isinstance(cmds, List | Tuple):
            if len(cmds) == 0:
                self.cmds: List[TokensContainer] = []
            elif isinstance(cmds[0], Token):
                self.cmds = [TokensContainer(*cmds)]
            elif isinstance(cmds[0], TokensContainer):
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

class Alias(EmptyStatement):
    def __init__(self, kw, kw_replace):
        self.kw: Token = kw
        self.kw_replace: Token = kw_replace

    def _apply_token(self, token: Token):
        if self.kw == token:
            return self.kw_replace

    def apply(self, cmd: TokensContainer):
        return TokensContainer(*(self._apply_token(token) for token in cmd))
        
# class ArgAliases(Alias):
#     def __init__(self, *args):
#         self.args = args
#         self.kw = self.default()

#     @staticmethod
#     def default(i):
#         return VarToken(Selector(), f'_{i}')

class Arg(TokensRef):
    def __init__(self, i, type_=ArgType.UNKOWN):
        self.i = i
        self.type_ = type_

class Args:
    def __init__(self, fun=None):
        if fun is None:
            if GLOBALS.fun is None:
                raise Exception('Args() initialized outside of a Fun')
            fun = GLOBALS.fun
        self.fun: Fun = fun
        self.args = [Arg(0, type_) for type_ in self.fun.in_types]

    def __iter__(self):
            return self.args.__iter__()
            # return (Arg(0, type_) for type_ in self.fun.in_types)

class FunStatement(Statement):
    def __init__(self, fun: 'Fun'):
        self.fun = fun
        self.cmds = [TokensContainer(FunctionToken(self.fun.namespace, self.fun.path))]
        self.idx = None

    def clear(self):
        pass
    
    def __call__(self, *args):
        super().__init__(self.cmds, add=True)
        # vals = (Value(val, type=in_type) for in_type, val in zip(self.fun.in_types, args))
        
        # if isinstance(self.fun.block.statements[0], ArgNames):
        #     funct_arg_names = self.fun.block.statements[0]
        #     self.fun.block.statements = self.fun.block.statements[1:]
        #     assignments = {funct_arg_name: val for funct_arg_name, val in zip(funct_arg_names, vals)}
        # else:
        #     assignments = {ArgNames.default(i): arg for i, arg in enumerate(args)}
        
        # for statement in self.fun.block.statements:
        #     pass


class Fun:
    def __init__(self, name: Optional[str] = None,
                # namespace: Optional[str] = None,
                # path: Optional[List[str]] = None
                 ):
        
        if name is None:
            self.name = GLOBALS.gen_name()
        else:
            self.name = name
        self.namespace = None
        self.path = None
        
        self.inline = True
        self.inline_block = None        

        self.out_types: Tuple[ArgType] | ArgType | None = None
        self.in_types: Tuple[ArgType] | ArgType | None = None
        
        self.refs = []
    
    @classmethod
    def get(cls, name: Optional[str], namespace: Optional[str] = None, path: Optional[List[str]] = None) -> FunStatement:
        return FunStatement(cls(name=name, namespace=namespace, path=path))

    def __class_getitem__(self, types):
        if isinstance(types, tuple):
            self.out_types = tuple(ArgType.from_type(t) for t in types)
        else:
            self.out_types = ArgType.from_type(types)
        return self

    def __getitem__(self, types):
        if isinstance(types, tuple):
            self.in_types = tuple(ArgType.from_type(t) for t in types)
        else:
            self.in_types = ArgType.from_type(types)
        return self
    
    def __enter__(self) -> Self | Tuple[Self, Arg] | Tuple[Self, Args]:
        self.inline = False
        GLOBALS.enter_path(self.name)
        self.parent = GLOBALS.fun
        GLOBALS.fun = self
        self.namespace = GLOBALS.namespace
        self.path = copy(GLOBALS.path)  # need to copy or else since path is a List object this will be a reference
        print_debug(f'curr path {self.path}')
        if self.in_types is None:
            return self
        elif isinstance(self.in_types, ArgType):
            return self, Arg(0, self.in_types)
        else:
            return self, Args(self)
    
    def __exit__(self, *args):
        GLOBALS.exit_path(self.name)
        GLOBALS.fun = self.parent
       
    def __call__(self, *args) -> FunStatement:
        if self.inline:
            if self.inline_block is None:
                self.inline_block = Block(*args)
                self.inline_block.clear()

                with self:
                    for statement in self.inline_block.statements:
                        GLOBALS.add_cmd(statement)

                # with Namespace(self.namespace, self.path):
                #     for statement in self.inline_block.statements:
                #         for cmd in statement.get_cmds():
                #             idx = GLOBALS.add_cmd(cmd)
                            # self.idxes.append(idx)

                return FunStatement(self)
            else:
                raise ValueError('Function block already assigned')
        else:
            print_debug(f'outline function call {self.namespace}:{'/'.join(self.path)}')
            fun_statement = FunStatement(self)
            fun_statement.__call__(*args)
            return fun_statement
    
    @staticmethod
    def wrap_tokens(tokens: List[Token]) -> List[Token]:
        uuid = uuid4()
        namespace = GLOBALS.namespace
        with Pathspace(str(uuid)):
            GLOBALS.add_cmd(TokensContainer(*tokens))
            path = GLOBALS.path
        return FunctionToken(namespace, path)

class SimpleFun:
    def __init__(self, name: Optional[str] = None):
        if name is None:
            self.name = GLOBALS.gen_name()
        else:
            self.name = name
        self.namespace = None
        self.path = None
        self.block = None
    
    
        

# def resolve_refs() -> List[Command]:
#     cmds = deepcopy(GLOBALS.cmds)
#     for _, file_cmds in cmds.items():
#         [(cmd.resolve() if isinstance(cmd, CommandRef) else cmd) for cmd in file_cmds if cmd is not None]
#     return cmds

def compile_program(program: Program, **serialize_kwargs):
    aliases = []

    for cmd in program:
        if isinstance(cmd, Alias):
            raise NotImplementedError()  # aliases.append(cmd)


    return program.serialize(**serialize_kwargs)

def compile_all(programs: Dict[str, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', write=False, color=False, debug=False) -> Dict[str, str]:
    out_files: Dict[Path, str] = {}
    for file_path, program in programs.items():
        if any(file_cmd is not None for file_cmd in program):
            file_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction\n'
            out_files[file_path] = compile_program(program, color=color, debug=debug)
            if write:
                file_path = Path(file_path)
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

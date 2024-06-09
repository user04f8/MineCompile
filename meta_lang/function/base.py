from copy import copy
from enum import Enum
from typing import List, Optional, Dict, Set
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
            self.idx = GLOBALS.add_statement(self)
        else:
            self.idx = None

    def get_cmds(self) -> List[TokensContainer]:
        return self.cmds
    
    def clear(self):
        if self.idx is not None:
            GLOBALS.clear_cmd(self.idx)

class WithStatement(Statement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        GLOBALS.blocks.append(self)
        self.args_from_global = []

    def add_statement(self, statement: Statement):
        self.args_from_global.append(statement)

    def __exit__(self, *args):
        GLOBALS.blocks.pop()
        self(*self.args_from_global)


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
    
    def cmds_to_global(self):
        for statement in self.statements:
            GLOBALS.add_statement(statement)
    
    def __len__(self):
        return len(self.statements)
    
    def clear(self):
        for statement in self.statements:
            statement.clear()

class ArgType(Enum):
    STATIC = 0
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
            case _:
                return ArgType.UNKOWN
    
    def cast(self, x):
        match self:
            case ArgType.INT:
                return Int32(x)
            case _:
                raise TypeError(f"Type {self} doesn't support input {x}")
            
class ValueRef:
    pass
    # def __init__(self, x, type: Optional[ArgType]):
    #     if type is None:
    #         self.type = ArgType.infer(x)
    #     else:
    #         x = type.cast(x)
    #         self.type = type
    #     self.x = x

class StaticValueRef:
    def __class_getitem__(self, static_type):
        self.static_type = static_type


class Arg(TokensRef):
    def __init__(self, i, type_):
        self.i = i
        self.type_: ValueRef | StaticValueRef
        if not isinstance(type_, ValueRef):
            self.type_ = StaticValueRef[type_]

class Args:
    def __init__(self, fun=None):
        if fun is None:
            if GLOBALS.fun is None:
                raise Exception('Args() initialized outside of a Fun')
            fun = GLOBALS.fun
        self.fun: Fun = fun
        self.args = [(Arg(0, type_) if isinstance(type_, ValueRef) else type_()) for type_ in self.fun.in_types]

    def __iter__(self):
            return self.args.__iter__()

class FunStatement(Statement):
    def __init__(self, fun: 'Fun'):
        self.fun = fun
        self.cmds = [TokensContainer(FunctionToken(self.fun.namespace, self.fun.path))]
        self.idx = None
    
    def __call__(self, *args):
        super().__init__(self.cmds, add=True)
        self.fun._attach_fun_ref(path=GLOBALS.get_full_path())

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
        self.namespace = GLOBALS.namespace
        self.path = GLOBALS.path + [self.name]
        
        self.inline = True
        self.inline_block = None        

        self.out_types: Tuple[ArgType] | ArgType | None = None
        self.in_types: Tuple[ArgType] | ArgType | None = None

        self.ref = None
        
        self.refs = set()
    
    @classmethod
    def get_statement(cls, name: Optional[str], namespace: Optional[str] = None, path: Optional[List[str]] = None) -> FunStatement:
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
        assert self.namespace == GLOBALS.namespace
        assert self.path == GLOBALS.path
        # self.namespace = GLOBALS.namespace
        # self.path = copy(GLOBALS.path)  # need to copy or else since path is a List object this will be a reference

        self.parent = GLOBALS.fun
        GLOBALS.fun = self
        self.ref, _ = self._gen_ref()
        if self.in_types is None:
            return self
        elif isinstance(self.in_types, ArgType):
            return self, Arg(0, self.in_types)
        else:
            return self, Args(self)
        
    @staticmethod
    def _gen_ref(path=None, attrs: tuple = ()) -> Tuple[Tuple[str, str], Tuple[str, ...]]:
        if path:
            return ('function', path), attrs
        else:
            return ('function', GLOBALS.get_full_path()), attrs
    
    def __exit__(self, *args):
        GLOBALS.exit_path(self.name)
        GLOBALS.fun = self.parent
       
    def __call__(self, *args) -> FunStatement:
        if self.inline:
            if self.inline_block is None:
                self.inline_block = Block(*args)
                self.inline_block.clear()

                fun_statement = FunStatement(self)
                # fun_statement.__call__(*args)
                return fun_statement
            else:
                raise ValueError('Function block already assigned')
        else:
            print_debug(f'implicit function->function_statement call {self.namespace}:{'/'.join(self.path)}')
            fun_statement = FunStatement(self)
            fun_statement.__call__(*args)
            return fun_statement
    
    @classmethod
    def _wrap_tokens(cls, tokens: List[Token]) -> Token:
        namespace = GLOBALS.namespace
        caller_ref = cls._gen_ref()
        with Pathspace(GLOBALS.gen_name()):
            callee_ref, _ = cls._gen_ref(attrs=('no_unwrap',))
            GLOBALS.add_statement(TokensContainer(*tokens))
            path = copy(GLOBALS.path)
            if caller_ref in GLOBALS.ref_graph:
                GLOBALS.ref_graph[callee_ref].add(caller_ref)
            else:
                GLOBALS.ref_graph[callee_ref] = {caller_ref}

        return FunctionToken(namespace, path)
    
    def _attach_hook(self, hook: str):
        print_debug(f'attaching hook to {self.name}: {hook}')
        self._attach_ref(
            (('$extern', hook), ())
        )
        if hook not in GLOBALS.fun_hooks:
            GLOBALS.fun_hooks[hook] = {self}
        else:
            GLOBALS.fun_hooks[hook].add(self)

    def _attach_fun_ref(self, path: str):
        self._attach_ref(self._gen_ref(path=path))
    
    def _attach_ref(self, ref: Tuple[Tuple[str, str], Tuple[str, ...]]):
        print_debug(f'attaching ref to {self.name}: {ref}')
        self.refs.add(ref)
        if self.ref in GLOBALS.ref_graph:
            GLOBALS.ref_graph[self.ref].add(ref)
        else:
            GLOBALS.ref_graph[self.ref] = {ref}

class PublicFun(Fun):
    def __init__(self, name: str):
        super().__init__(name=name)

    def __enter__(self):
        out = super().__enter__()
        self._attach_hook('%PUBLIC%')
        return out

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
    s = program.serialize(**serialize_kwargs)
    # post-processing
    s = s.replace(REMOVE_TOKEN_SEP + TOKEN_SEP, '')
    return s

def compile_all(programs: Dict[str, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', write=False, color=False, debug=False) -> Dict[str, str]:
    # prune refs
    for hook, hooked_fun in GLOBALS.fun_hooks.items():
        hook: str
        hooked_fun: Fun
        pass
    def prune_refs(graph: Dict[Tuple[str, str], Set[Tuple[Tuple[str, str], Tuple[str, ...]]]]):
        def dfs_to_extern(source: Tuple[str, str], discovered: Set[Tuple[str, str]] = set()) -> Optional[str]:
            print_debug(f'dfs call at node {source} {discovered}')
            if source not in graph.keys():
                print_warn(f'invalid ref: {source}')
                return None
            for u, u_attrs in graph[source]:
                if u[0] == '$extern':
                    return u[1]
                    # external ref reached
                if u not in discovered:
                    discovered.add(u)
                    extern_ref = dfs_to_extern(u, discovered)
                    if extern_ref:
                        print_debug(f'dfs return at node {source} {discovered}')
                        return extern_ref
            print_debug(f'dfs return at node {source} {discovered}')
            return None
        
        for fun_path in programs.keys():
            u = ('function', fun_path)
            extern_ref = dfs_to_extern(u)
            print_debug(f'external_ref for {u}: {extern_ref}')
            if extern_ref is None:
                match u:
                    case ('function', path):
                        if GLOBALS.programs[path].cmds:
                            print_warn(f'Pruning unreferenced function at {path}')
                            print_debug(f'cmds: {GLOBALS.programs[path].cmds}')
                        programs[path].remove()
                        
        
        pass
    prune_refs(GLOBALS.ref_graph)

    

    
    
    
    
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


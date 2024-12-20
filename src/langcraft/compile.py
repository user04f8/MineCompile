from pathlib import Path
from zipfile import ZipFile
from random import randint
from typing import Any, Callable, Dict, List, Tuple
import json

from .globals import GLOBALS, DATAPACK_ROOT, RefFlags
from .debug_utils import print_debug, print_warn, print_debug_colorful
from .json_utils import JSON
from .serialize import REMOVE_TOKEN_SEP, TOKEN_SEP, Program, serialize_function_name
from .base import Fun, FunStatement, Namespace, WithStatement
from .commands import _ExecuteContainer, RawExecute
from .load import load

PRUNE_INLINE = False  # TODO need to update optim
PRUNE_INLINE_EXECUTE = False

def compile_program(program: Program, debug=True, **serialize_kwargs):
    if debug:
        print_debug(f'compiling {program}')
    s = program.serialize(debug=debug, **serialize_kwargs)
    s = s.replace(REMOVE_TOKEN_SEP + TOKEN_SEP, '')
    return s

Ref = Tuple[str, str]

def ref_to_program(ref: Ref) -> Program | None:
    match ref:
        case ('function', fun_path):
            return GLOBALS.programs.get(fun_path)
    return None

def fun_path_to_ref(fun_path: str):
    return 'function', fun_path

def traverse(source: Ref, discovered=None, discovered_and_removed=None, depth=0):
    if discovered_and_removed is None:
        discovered_and_removed = set()
    if discovered is None:
        discovered = set()
    source_children = GLOBALS.ref_graph.get(source, {})
    source_program = ref_to_program(source)

    print_debug_colorful('|   '*(depth - 1) + ('|---' if depth > 0 else '') + source[1].replace('$root/', ''), 'blue')

    children_removed = True
    for u in source_children:
        if u in discovered:
            children_removed |= u in discovered_and_removed
        else:
            discovered.add(u)
            remove_u = traverse(u, discovered, discovered_and_removed, depth=depth+1)
            if remove_u:
                discovered_and_removed.add(remove_u)
            children_removed |= remove_u
    
    if children_removed:
        removable = PRUNE_INLINE
        unwrap_single_line = False
        for parent, parent_type in GLOBALS.backwards_ref_graph[source].items():
            print_debug_colorful('|   '*depth + r'\___' + parent[1].replace('$root/', '') + '   \t' + str(parent_type), 'light_grey')
            parent_program = ref_to_program(parent)
            if not parent_program:
                if parent[0] not in {'$extern'}:
                    print_warn(f'unable to find {parent} as funct from ref_graph')
                removable = False
            elif not (parent_type ^ RefFlags.NONE):
                pass  # nothing to do here
            elif PRUNE_INLINE_EXECUTE and not (parent_type ^ RefFlags.EXECUTE) or not (parent_type ^ RefFlags.WITH_BLOCK):
                n_lines = len(source_program.serialize().split('\n'))
                if n_lines == 1:
                    unwrap_single_line = True
                if n_lines > 1:
                    removable = False
            else:
                removable = False
            
        if removable:
            for parent, parent_type in GLOBALS.backwards_ref_graph[source].items():
                parent_program = ref_to_program(parent)  # cannot be None
                j = 0
                for i, cmd in enumerate(parent_program.cmds):
                    if isinstance(cmd, FunStatement):
                        fun_cmds = GLOBALS.programs[GLOBALS.get_function_path(cmd.fun.namespace, cmd.fun.path)].cmds
                        parent_program.unwrap_to(i + j, fun_cmds)
                        j += len(fun_cmds) - 1
                    elif unwrap_single_line and isinstance(cmd, WithStatement):
                        if not cmd._unwrapped:
                            fun_cmd, = source_program.cmds
                            # cmd._unwrap_statement(source, fun_cmd.tokenize(), _ExecuteContainer=_ExecuteContainer)
                            single_line_tokens = fun_cmd.tokenize()
                            for cmd_ in cmd.cmds:
                                if isinstance(cmd_, _ExecuteContainer):
                                    fun_token = cmd_.get_fun_token()
                                    if fun_token is None:
                                        print_warn(f'already unwrapped {source}')
                                    else:
                                        fun_path = GLOBALS.get_function_path(fun_token.namespace, fun_token.path)
                                        if fun_path == source[1]:
                                            assert cmd_._block_tokens != []
                                            cmd_._block_tokens[1:] = single_line_tokens
                                            cmd._unwrapped = True
                    elif unwrap_single_line and isinstance(cmd, RawExecute):
                        fun_cmd, = source_program.cmds
                        execute_container: _ExecuteContainer = cmd._get_cmds()[-1]
                        execute_container._block_tokens[1:] = fun_cmd.tokenize()
                    else:
                        print_debug(f'ignoring cmd in unwrap: {cmd} {type(cmd)}')
    else:
        removable = False

    print_debug_colorful('|   '*(depth - 1) + ('|---' if depth > 0 else '') + source[1].replace('$root/', ''), ('red' if removable else 'green'))
    
    if source_program := ref_to_program(source):
        source_program.used = not removable
    
    return removable

def save_files(root_dir: str, write_files: dict):
    for file_full_path, file_contents in write_files.items():
        file_full_path = Path(root_dir + file_full_path)
        file_full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_full_path, 'w') as f:
            f.write(file_contents)

def save_files_to_zip(root_dir: str, write_files: dict[str, str]):
    zip_file_path = Path(root_dir + '.zip')
    zip_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with ZipFile(zip_file_path, 'w') as zipf:
        for file_path, content in write_files.items():
            zipf.writestr(file_path, content)

def compile_all(programs: Dict[str, Program] | None = None,
                structures: Dict[str, Any] | None = None,
                jsons: Dict[str, JSON] | None = None,
                root_dir: str = '../datapacks/compile_test',
                write=False,
                color=False,
                debug=False,
                optim=True,
                save_strategy: Callable[[str, dict[str, str]], None] = save_files_to_zip
                ) -> Dict[str, str]:
    if programs is None:
        programs = GLOBALS.programs
    if jsons is None:
        jsons = GLOBALS.jsons


    root_dir = root_dir.replace('$rand', hex(randint(0, 65535)))
    data_dir = 'data'

    # prune refs
    for hook, hooked_funs in GLOBALS.fun_hooks.items():
        hook: str
        hooked_funs: Fun
        if hook[0] == '#':
            namespace, tag_path = hook[1:].split(':')
            with Namespace(name=namespace, full_path=tag_path.split('/')):
                hooked_fun_names = [serialize_function_name(hooked_fun.namespace, hooked_fun.path) for hooked_fun in hooked_funs]
                GLOBALS.add_to_function_tag(None, hooked_fun_names)

    if optim:
        for program in programs.values():
            program.optimize()

        for caller, callees in GLOBALS.ref_graph.items():
            match caller:
                case ('$extern', _):
                    for callee in callees:
                        traverse(callee)
        
        for program in programs.values():
            program.optimize()
    else:
        for program in programs.values():
            program.used = True

    valid_fun_refs = [path for path, program in programs.items() if program.used]
    valid_json_refs = [path for path, _ in jsons.items()]

    def validate_fun_ref(namespace: str, path: List[str]):
        return GLOBALS.get_function_path(namespace, path) in valid_fun_refs

    def validate_json_ref(namespace: str, path: List[str]):
        return GLOBALS.get_json_path(namespace, path) in valid_json_refs

    out_files: Dict[str, str] = {}
    write_files: Dict[str, str] = {'pack.mcmeta': json.dumps({
        "pack": {
            "description": "Autogenerated by langcraft v0.1",
            "pack_format": 47
        }
    })}
    # pack.mcmeta

    # json
    for file_path, json_ in jsons.items():
        out_files[file_path] = json_.serialize(debug=debug, color=color, validate_fun=validate_fun_ref, validate_json=validate_json_ref)
        if write:
            file_full_path = file_path.replace(DATAPACK_ROOT, data_dir) + '.json'
            write_files[file_full_path] = out_files[file_path]
    # TODO nbt structures
                
    # function:serialize
    for file_path, program in programs.items():
        if program.used:
            out_files[file_path] = compile_program(program, color=color, debug=debug, validate_fun=validate_fun_ref, validate_json=validate_json_ref)
            if write:
                file_full_path = file_path.replace(DATAPACK_ROOT, data_dir) + '.mcfunction'
                write_files[file_full_path] = out_files[file_path]

    if write:
        save_strategy(root_dir, write_files)

    return out_files

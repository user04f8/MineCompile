from copy import deepcopy
from pathlib import Path
from random import randint
from typing import Any, Optional, Set, Tuple


from .globals import GLOBALS, DATAPACK_ROOT
from .debug_utils import *
from .json_utils import JSON
from .serialize import *
from .base import Fun, FunStatement, Namespace, Statement
from .commands import _ExecuteContainer

def compile_program(program: Program, **serialize_kwargs):
    print_debug(f'compiling {program}')

    s = program.serialize(**serialize_kwargs)
    # post-processing
    s = s.replace(REMOVE_TOKEN_SEP + TOKEN_SEP, '')
    return s

def compile_all(programs: Dict[str, Program] = GLOBALS.programs, structures: Dict[str, Any] = None, jsons: Dict[str, JSON] = GLOBALS.jsons, root_dir: str = '../datapacks/compile_test/data', write=False, color=False, debug=False, max_optim_steps=20) -> Dict[str, str]:
    root_dir = root_dir.replace('$rand', hex(randint(0, 65535)))
    
    # prune refs
    for hook, hooked_funs in GLOBALS.fun_hooks.items():
        hook: str
        hooked_funs: Fun
        if hook[0] == '#':
            # handle tags
            namespace, tag_path = hook[1:].split(':')
            with Namespace(name=namespace, full_path=tag_path.split('/')):
                hooked_fun_names = [serialize_function_name(hooked_fun.namespace, hooked_fun.path) for hooked_fun in hooked_funs]
                GLOBALS.add_to_function_tag(None, hooked_fun_names)

    def prune_refs(graph: Dict[Tuple[str, str], Set[Tuple[str, str]]]):
        graph_update = True
        while graph_update:
            graph_update = False
            for fun_path, fun_program in programs.items():
                if fun_program.unused:
                    continue  # skip all discovered unused functions
                u = ('function', fun_path)
                if u not in graph:
                    fun_program.mark_unused()
                    continue
                vs = graph[u]
                if any(v[0] == '$extern' for v in vs):
                    continue  # skip all direct external hooks
                if any(v[0] not in ('function',) for v in vs):
                    continue  # skip all unhandled refs
                backwards = [u_ for u_, vs_ in graph.items() if u in vs_]
                if len(backwards) == 0:  # first find root nodes / leaf nodes at the reversal of the graph
                    for v in vs:
                        match v:
                            case ('function', v_fun_path):
                                v_fun_program = programs[v_fun_path]
                                j = 0
                                for i, cmd in enumerate(v_fun_program):
                                    if isinstance(cmd, FunStatement) \
                                            and GLOBALS.get_function_path(cmd.fun.namespace, cmd.fun.path) == v_fun_path:
                                        v_fun_program.unwrap_to(i + j, fun_program.cmds)
                                        j += len(fun_program.cmds) - 1
                                graph[u].remove(v)
                                graph_update = True
        
        def dfs_to_extern(source: Tuple[str, str], discovered: Set[Tuple[str, str]]) -> Optional[str]:
            if source not in graph.keys():
                return None
            
            for u in graph[source]:
                if u[0] == '$extern':
                    return u[1]
                    # external ref reached
                if u not in discovered:
                    discovered.add(u)
                    extern_ref = dfs_to_extern(u, discovered)
                    if extern_ref:
                        return extern_ref
            return None
        
        for fun_path, fun_program in programs.items():
            if not fun_program.unused:
                u = ('function', fun_path)
                extern_ref = dfs_to_extern(u, set())
                if extern_ref is None:
                    if fun_program.cmds:
                        fun_serial = fun_program.serialize()
                        print_warn(f'Pruning unreferenced function at {fun_path}: {fun_serial[:32].replace('\n', ' || ')}{'...' if len(fun_serial) > 32 else ''}')
                    fun_program.mark_unused()

    prune_refs(deepcopy(GLOBALS.ref_graph))

    # validate = Validate()
    valid_fun_refs = [path for path, program in programs.items() if not program.unused]
    valid_json_refs = [path for path, json in jsons.items()]

    def validate_fun_ref(namespace: str, path: List['str']):
        return GLOBALS.get_function_path(namespace, path) in valid_fun_refs

    def validate_json_ref(namespace: str, path: List['str']):
        return GLOBALS.get_json_path(namespace, path) in valid_json_refs
    out_files: Dict[str, str] = {}

    # json
    for file_path, json_ in jsons.items():
        out_files[file_path] = json_.serialize(debug=debug, color=color, validate_fun=validate_fun_ref, validate_json=validate_json_ref)
        if write:
            file_full_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.json'
            file_full_path = Path(file_full_path)
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_full_path, 'w') as f:
                f.write(out_files[file_path])

    # TODO nbt structures
                
    # function:serialize
    for file_path, program in programs.items():
        if any(file_cmd is not None for file_cmd in program) and not program.unused:
            out_files[file_path] = compile_program(program, color=color, debug=debug, validate_fun=validate_fun_ref, validate_json=validate_json_ref)
            if write:
                file_full_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction'
                file_full_path = Path(file_full_path)
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_full_path, 'w') as f:
                    f.write(out_files[file_path])

    return out_files


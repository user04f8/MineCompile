from .base import *
from .commands import _ExecuteContainer

def compile_program(program: Program, **serialize_kwargs):
    print_debug(f'compiling {program}')

    s = program.serialize(**serialize_kwargs)
    # post-processing
    s = s.replace(REMOVE_TOKEN_SEP + TOKEN_SEP, '')
    return s

def compile_all(programs: Dict[str, Program] = GLOBALS.programs, structures: Dict[str, Any] = None, jsons: Dict[str, JSON] = GLOBALS.jsons, root_dir: str = './datapacks/testing/data', write=False, color=False, debug=False, max_optim_steps=20) -> Dict[str, str]:
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

    def prune_refs(graph: Dict[Tuple[str, str], Set[Tuple[Tuple[str, str], Tuple[str, ...]]]]):
        def dfs_to_extern(source: Tuple[str, str], discovered: Set[Tuple[str, str]]) -> Optional[str]:
            if source not in graph.keys():
                return None
            for u, u_attrs in graph[source]:
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
            u = ('function', fun_path)
            extern_ref = dfs_to_extern(u, set())
            # print_debug(f'external_ref for {u}: {extern_ref}')
            if extern_ref is None:
                match u:
                    case ('function', path):
                        if programs[path].cmds:
                            fun_serial = programs[path].serialize()
                            print_warn(f'Pruning unreferenced function at {path}: {fun_serial[:32].replace('\n', ' || ')}{'...' if len(fun_serial) > 32 else ''}')
                        programs[path].mark_unused()    

    def unwrap_cmd(cmd: Statement):
        if isinstance(cmd, FunStatement):
            fun_path = GLOBALS.get_function_path(cmd.fun.namespace, cmd.fun.path)
            refs = GLOBALS.ref_graph[('function', fun_path)]
            if len(refs) > 1:
                # if a function has multiple refs, skip it
                return
            if any(ref[0] == '$extern' for ref, attrs in refs):
                # if a function has direct external references, skip it 
                return
            programs[fun_path].mark_unused()  # program has one ref and was unwrapped
            return [cmd for cmd in programs[fun_path].cmds]
            # del GLOBALS.ref_graph[('function', fun_path)]  
        elif isinstance(cmd, _ExecuteContainer):
            fun_token = cmd.get_fun_token()
            if fun_token:
                fun_path = GLOBALS.get_function_path(fun_token.namespace, fun_token.path)
                refs = GLOBALS.ref_graph[('function', fun_path)]
                if len(refs) > 1:
                    # if a function has multiple refs, skip it
                    return
                if any(ref[0] == '$extern' for ref, attrs in refs):
                    # if a function has direct external references, skip it 
                    return
                fun_cmd, *tmp = [cmd for cmd in programs[fun_path].cmds]
                if not tmp:
                    if isinstance(fun_cmd, TokensRef):
                        fun_cmd, *tmp = fun_cmd.resolve()
                        if not tmp:
                            print_debug(f'function resolves to single command `{fun_cmd}` (clearing refs)')
                            programs[fun_path].mark_unused()  # program has one ref and was unwrapped
                            return fun_cmd
        elif isinstance(cmd, Statement):
            # unwrap all other TokensRefs
            for i, inner_cmd in enumerate(cmd.cmds):
                new_cmd = unwrap_cmd(inner_cmd)
                if isinstance(new_cmd, TokensContainer):
                    print_debug(f'set cmd {cmd.cmds[i]} to {new_cmd}')
                    if isinstance(cmd.cmds[i], _ExecuteContainer):
                        cmd.cmds[i]._block_tokens = [CommandKeywordToken('run')] + new_cmd.tokens
                    else:
                        print_err('unreachable optim reached in unwrap_cmd')

    # function:optimize
    for _ in range(max_optim_steps):
        for program in programs.values():
            program.optimize()
        
        for program in programs.values():
            for i, cmd in enumerate(program):
                try:
                    new_cmd = unwrap_cmd(cmd)
                    if isinstance(new_cmd, list):
                        program.unwrap_to(i, new_cmd)
                    elif new_cmd:
                        print_err('outer new_cmd reached, likely raw _ExecuteContainer')
                except ValueError:
                    pass # TODO


    prune_refs(GLOBALS.ref_graph)
    
    if debug:
        # display refs
        print_debug(f'ref graph: {GLOBALS.ref_graph}')
    
    out_files: Dict[str, str] = {}
                
    # function:serialize
    for file_path, program in programs.items():
        if any(file_cmd is not None for file_cmd in program) and not program.unused:
            out_files[file_path] = compile_program(program, color=color, debug=debug)
            if write:
                file_full_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.mcfunction'
                file_full_path = Path(file_full_path)
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_full_path, 'w') as f:
                    f.write(out_files[file_path])

    # json
    for file_path, json_ in jsons.items():
        out_files[file_path] = json_.serialize(debug=debug, color=color)
        if write:
            file_full_path = file_path.replace(DATAPACK_ROOT, root_dir) + '.json'
            file_full_path = Path(file_full_path)
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_full_path, 'w') as f:
                f.write(out_files[file_path])

    # TODO nbt structures


    return out_files


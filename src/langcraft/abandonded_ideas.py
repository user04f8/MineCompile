### base.py

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


def prune_refs(graph: Dict[Tuple[str, str], Set[Tuple[str, str]]]):
    # clean graph
    for key, vs in graph.items():
        graph[key] = {v for v in vs if v in graph.keys() or v[0] == '$extern'}
    
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
        u = ('function', fun_path)
        extern_ref = dfs_to_extern(u, set())
        # print_debug(f'external_ref for {u}: {extern_ref}')
        if extern_ref is None and not fun_program.unused:
            if fun_program.cmds:
                fun_serial = fun_program.serialize()
                print_warn(f'Pruning unreferenced function at {fun_path}: {fun_serial[:32].replace('\n', ' || ')}{'...' if len(fun_serial) > 32 else ''}')
            fun_program.mark_unused()

    return graph

def unwrap_cmd(cmd: Statement) -> Tuple[Optional[TokensContainer], List[Tuple[str, str]]]:
    if isinstance(cmd, FunStatement):
        fun_path = GLOBALS.get_function_path(cmd.fun.namespace, cmd.fun.path)
        if ('function', fun_path) not in GLOBALS.ref_graph:
            print_err(f'unable to unwrap cmd not in GLOBALS.ref_graph: {fun_path}')
            return None, []
        refs = GLOBALS.ref_graph[('function', fun_path)]
        if len(refs) > 1:
            # if a function has multiple refs, skip it
            return None, []
        if any(ref[0] == '$extern' for ref in refs):
            # if a function has direct external references, skip it 
            return None, []
        refs_from_unwrapped_fun = [ref0 for ref0, ref1s in GLOBALS.ref_graph.items() if any(ref1 == ('function', fun_path) for ref1 in ref1s)]
        if len(refs_from_unwrapped_fun) > 1:
            print_err(refs_from_unwrapped_fun)
            return None, []

        # del GLOBALS.ref_graph[('function', fun_path)] # function had a single ref and does not ref anything else
        programs[fun_path].mark_unused()  # (hides warnings)
        return [cmd for cmd in programs[fun_path].cmds], [] #refs_from_unwrapped_fun
    elif isinstance(cmd, _ExecuteContainer):
        fun_token = cmd.get_fun_token()
        if fun_token:
            fun_path = GLOBALS.get_function_path(fun_token.namespace, fun_token.path)
            if ('function', fun_path) not in GLOBALS.ref_graph:
                return None, []
            refs = GLOBALS.ref_graph[('function', fun_path)]
            refs: set
            if len(refs) > 1:
                # if a function has multiple references, skip it
                return None, []
            if any(ref[0] == '$extern' for ref in refs):
                # if a function has direct external references, skip it 
                return None, []
            fun_cmd, *tmp = [cmd for cmd in programs[fun_path].cmds]
            if not tmp:
                if isinstance(fun_cmd, TokensRef):
                    fun_cmd, *tmp = fun_cmd.resolve()
                    if not tmp:
                        print_debug(f'function resolves to single command `{fun_cmd}` (clearing refs)')
                        new_refs = []
                        for fun_caller in GLOBALS.ref_graph:
                            if fun_caller == ('function', fun_path): # if fun_caller references unwrapped function
                                new_refs.append(fun_caller)
                        # del GLOBALS.ref_graph[('function', fun_path)] # function had a single ref and is now unreferenced
                        programs[fun_path].mark_unused()  # (hides warnings)
                        return fun_cmd, new_refs
    elif isinstance(cmd, Statement):
        # unwrap all other TokensRefs
        for i, inner_cmd in enumerate(cmd.cmds):
            new_cmd, new_refs = unwrap_cmd(inner_cmd)
            if isinstance(new_cmd, TokensContainer):
                print_debug(f'set cmd {cmd.cmds[i]} to {new_cmd}')
                if isinstance(cmd.cmds[i], _ExecuteContainer):
                    cmd.cmds[i]._block_tokens = [CommandKeywordToken('run')] + new_cmd.tokens
                else:
                    print_err('unreachable optim reached in unwrap_cmd')
            return None, new_refs
    return None, []

# function:optimize
for _ in range(max_optim_steps):
    for program in programs.values():
        program.optimize()
    
    for fun_path, program in programs.items():
        if ('function', fun_path) not in GLOBALS.ref_graph:
            program.mark_unused()
        if program.unused:
            continue
        j = 0
        for i, cmd in enumerate(program):
            try:
                new_cmd, new_refs = unwrap_cmd(cmd)
                # for new_ref in new_refs:
                #     if new_ref in GLOBALS.ref_graph:
                #         GLOBALS.ref_graph[new_ref].add(('function', fun_path))
                #     else:
                #         print_warn(f'new reference {new_ref} added to GLOBALS.ref_graph in optim')
                #         GLOBALS.ref_graph[new_ref] = {('function', fun_path)}
                if isinstance(new_cmd, list):
                    program.unwrap_to(i + j, new_cmd)
                    j += len(new_cmd) - 1
                elif new_cmd:
                    print_err('outer new_cmd reached, likely raw _ExecuteContainer')
            except ValueError:
                pass # TODO

    # for fun_path, program in programs.items():
    #     if program.unused:
    #         if ('function', fun_path) in GLOBALS.ref_graph:
    #             del GLOBALS.ref_graph[('function', fun_path)]

    prune_refs(GLOBALS.ref_graph)
if debug:
    print_debug(f'pruned refs: {GLOBALS.ref_graph}')


# def prune_unused_functions(programs: Dict[str, Program], graph: Dict[Ref, Set[Ref]]):
#     """
#     Mark unused functions and update the function graph.
#     """
#     graph_update = True
#     while graph_update:
#         graph_update = False
#         for fun_path, fun_program in programs.items():
#             if fun_program.unused:
#                 continue  # skip all discovered unused functions
#             u = ('function', fun_path)
#             if u not in graph:
#                 fun_program.mark_unused()
#                 continue
#             if any(v[0] == '$extern' for v in graph[u]):
#                 continue  # skip all direct external hooks
#             if any(v[0] not in ('function',) for v in graph[u]):
#                 continue  # skip all unhandled refs
#             backwards = [u_ for u_, vs_ in graph.items() if u in vs_]

#             if len(backwards) == 0:  # first find root nodes / leaf nodes at the reversal of the graph
#                 removable = True
#                 if len(fun_program.cmds) == 1:
#                     fun_single_cmd = fun_program.cmds[0]
#                 else:
#                     fun_single_cmd = None
#                 for v in graph[u]:
#                     new_vs = deepcopy(graph[u])
#                     match v:
#                         case ('function', v_fun_path):
#                             v_fun_program = programs[v_fun_path]
#                             j = 0
#                             func_calls = 0
#                             for i, cmd in enumerate(v_fun_program):
#                                 if isinstance(cmd, FunStatement):
#                                     if GLOBALS.get_function_path(cmd.fun.namespace, cmd.fun.path) == fun_path:
#                                         v_fun_program.unwrap_to(i + j, fun_program.cmds)
#                                         j += len(fun_program.cmds) - 1
#                                         func_calls += 1
#                                 elif isinstance(cmd, Statement):
#                                     for x in cmd.cmds:
#                                         if isinstance(x, _ExecuteContainer):
#                                             removable = False
#                                             if fun_single_cmd:
#                                                 x._block_tokens = [CommandKeywordToken('run'), *fun_single_cmd.tokenize()]
#                                                 func_calls += 1
#                                             else:
#                                                 removable = False
#                                 else:
#                                     print_err('optim found non statement')
#                             if func_calls == 0 and removable:
#                                 print_err(f'no func calls found in program {v_fun_path}:\n{v_fun_program.serialize(color=False)}\nmismatch between funct and ref_graph')
#                     if v in new_vs and removable:
#                         new_vs.remove(v)
#                         fun_program.mark_unused()
#                         graph_update = True
#                 graph[u] = new_vs

# def dfs_to_extern(source: Tuple[str, str], graph: Dict[Tuple[str, str], Set[Tuple[str, str]]], discovered: Set[Tuple[str, str]]) -> Optional[str]:
#     for u in graph.get(source, default=set()):
#         if u[0] == '$extern':
#             return u[1]
#         if u not in discovered:
#             discovered.add(u)
#             extern_ref = dfs_to_extern(u, graph, discovered)
#             if extern_ref:
#                 return extern_ref
#     return None
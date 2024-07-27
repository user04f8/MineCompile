from enum import IntEnum
from typing import Optional, Callable, Set, Tuple, List, Dict
import random
import string

from .serialize import Program
from .json_utils import *

DATAPACK_ROOT: str = '$root'

type Ref = Tuple[str, str]
class RefFlags(IntEnum):
    NONE = 0b0
    WITH_BLOCK = 0b1
    EXECUTE = 0b10

type ScoreSetup = str
type Setup = ScoreSetup

class Globals:
    def __init__(self, namespace='main'):
        self.debug = True
        self.namespace: str = namespace
        self.path: List[str] = []
        self.programs: Dict[str, Program] = {self.get_function_path(): Program()}
        self.structures: Dict[str] # TODO
        self.jsons: Dict[str, JSON] = {}

        self.fun = None
        self.blocks = []
        self.in_with = False

        self.setups: List[ScoreSetup] = []

        self.backwards_ref_graph: Dict[Ref, Dict[Ref, RefFlags]] = {}  # GLOBALS.ref_graph[callee_ref] = {caller_ref for caller_ref in caller_refs}
        self.ref_graph: Dict[Ref, Dict[Ref, RefFlags]] = {}  # GLOBALS.ref_graph[caller_ref] = {callee_ref for callee_ref in callee_refs}
        self.fun_hooks = {}
        self.resource_hooks = {} # TODO
        self.names: Dict[str, Set[str]] = {}

    def ref_call(self, caller_ref: Ref, callee_ref: Ref, ref_type: RefFlags = RefFlags.NONE):
        if caller_ref in self.ref_graph:
            if callee_ref in self.ref_graph[caller_ref]:
                self.ref_graph[caller_ref][callee_ref] |= ref_type
            else:
                self.ref_graph[caller_ref][callee_ref] = ref_type
        else:
            self.ref_graph[caller_ref] = {callee_ref: ref_type}
        if callee_ref in self.backwards_ref_graph:
            if caller_ref in self.backwards_ref_graph[callee_ref]:
                self.backwards_ref_graph[callee_ref][caller_ref] |= ref_type
            else:
                self.backwards_ref_graph[callee_ref][caller_ref] = ref_type
        else:
            self.backwards_ref_graph[callee_ref] = {caller_ref: ref_type}

    def ref_remap(self, removed_ref: Ref) -> None | Tuple[List[Ref], List[Ref]]:
        if removed_ref not in self.ref_graph:
            return
        
        parents = self.backwards_ref_graph.get(removed_ref, {})
        children = self.ref_graph.get(removed_ref, {})

        if any(child == removed_ref for child in children):
            return None  # failure due to recursive reference

        def or_dict(d1, d2):
            return {k1: v1 for k1, v1 in d1.items() if k1 not in d2} | {
                    k2: v2 for k2, v2 in d2.items() if k2 not in d1} | {
                    k: v1 | d2[k] for k, v1 in d1.items() if k in d2}  # to handle RefFlags
                
        # Connect each parent to each child
        for parent in parents:
            if parent not in self.ref_graph:
                self.ref_graph[parent] = {}
            self.ref_graph[parent] = or_dict(self.ref_graph[parent], children)
        
        for child in children:
            if child not in self.backwards_ref_graph:
                self.backwards_ref_graph[child] = {}
            self.backwards_ref_graph[child] = or_dict(self.ref_graph[child], parents)
        
        # Remove the removed_ref from the graphs
        if removed_ref in self.ref_graph:
            del self.ref_graph[removed_ref]
        if removed_ref in self.backwards_ref_graph:
            del self.backwards_ref_graph[removed_ref]
        
        # Remove any direct references to the removed_ref in parents and children
        for parent in parents:
            if parent in self.ref_graph:
                if removed_ref in self.ref_graph[parent]:
                    self.ref_graph[parent].remove(removed_ref)
        
        for child in children:
            if child in self.backwards_ref_graph:
                if removed_ref in self.ref_graph[child]:
                    self.backwards_ref_graph[child].remove(removed_ref)
        
        return children, parents
    
    def get_function_path(self, namespace=None, path=None):
        if namespace is None:
            namespace = self.namespace
        if path is None:
            path = self.path
        return '/'.join([DATAPACK_ROOT, namespace, 'function'] + path)
    
    # get_structure_path

    def get_json_path(self, folder: str, add_to_path: Optional[str] = None, namespace=None, path=None):
        if namespace is None:
            namespace = self.namespace
        if path is None:
            path = self.path
        return '/'.join([DATAPACK_ROOT, namespace, folder] + path + ([add_to_path] if add_to_path is not None else []))

    def set_namespace(self, namespace, new_path=None):
        self.namespace = namespace
        if new_path is not None:
            self.path = new_path
        
        # *folder_path_names, name = new_path
        # if self.namespace not in self.path_tree:
        #     self.path_tree[self.namespace] = {}
        # inner_tree = self.path_tree[self.namespace]
        # folder_path_name = folder_path_names.pop(0)
        # while folder_path_name in inner_tree:
        #     inner_tree = inner_tree[folder_path_name]
        #     folder_path_name = folder_path_names.pop(0)
        # for folder_path_name in folder_path_names:
        #     inner_tree[folder_path_name] = {}
        #     inner_tree = inner_tree[folder_path_name]
        self.add_current_path()

    def enter_path(self, name):
        self.path.append(name)

        # if name not in self.path_tree:
        #     self.path_tree[name] = {}
        self.add_current_path()

    def exit_path(self, name=None):
        exited_path = self.path.pop()
        if name is not None:
            assert exited_path == name, f'Path entered does not match path exited: {exited_path} != {name}'
        self.add_current_path()

    def add_current_path(self):
        if self.get_function_path() not in self.programs:
            self.programs[self.get_function_path()] = Program()

    def gen_function_name(self, default: str = 'x') -> str:
        for i in range(256):
            candidate_name = default + hex(i)[2:]
            if self.get_function_path(path=[*self.path, candidate_name]) not in self.programs:
                return candidate_name

        for i in range(8, 32): # 32 == len(uuid4().hex)
            candidate_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(i)) #uuid4().hex[:i]
            if self.get_function_path(path=[*self.path, candidate_name]) not in self.programs:
                return candidate_name
        assert False, 'Ran out of potential candidate names (candidate UUIDs not unique)'

    
    def gen_name(self, path) -> str:
        existing_names = self.names.get(path, set())
        for i in range(256):
            candidate_name = 'x' + hex(i)[2:]
            if candidate_name not in existing_names:
                if path not in self.names:
                    self.names[path] = {candidate_name}
                else:
                    self.names[path].add(candidate_name)
                return candidate_name

        for i in range(8, 32): # 32 == len(uuid4().hex)
            candidate_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(i))
            if candidate_name not in existing_names:
                if path not in self.names:
                    self.names[path] = {candidate_name}
                else:
                    self.names[path].add(candidate_name)
                return candidate_name
        assert False, 'Ran out of potential candidate names (candidate UUIDs not unique)'


    def add_statement(self, statement):
        if self.blocks == []:
            idx = len(self.programs[self.get_function_path()])
            self.programs[self.get_function_path()].append(statement)
            return (self.get_function_path(), idx)
        else:
            self.blocks[-1].add_statement(statement)
            return None

    def clear_cmd(self, pathed_idx):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = None

    def set_cmd(self, pathed_idx, cmd):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = cmd

    def set_json(self, folder: str, name: str, json: JSON):
        # full list of JSON things to bind https://minecraft.wiki/w/Data_pack
        self.jsons[self.get_json_path(folder, add_to_path=name)] = json

    def add_json(self, folder: str, name: str, json: JSON):
        path = self.get_json_path(folder, add_to_path=name)
        if path not in self.jsons:
            self.jsons[path] = json
        else:
            self.jsons[path].add(json)

    def strict_add_json(self, folder: str, name: Optional[str], json: JSON, base: Optional[Callable] = None):
        path = self.get_json_path(folder, add_to_path=name)
        if path not in self.jsons:
            if base is not None:
                self.jsons[path] = base()
                self.jsons[path].strict_add(json)
            self.jsons[path] = json
        else:
            self.jsons[path].strict_add(json)

    # TAGS
    def add_to_function_tag(self, name: Optional[str], function_names: List[str]):
        self.strict_add_json('tags/function', name, FunctionJSON(function_names), base=FunctionJSON)
    
    def set_tag(self, name, json, tag_type):
        # tag_type can be ['function', 'block', 'entity_type', 'fluid', 'game_event', 'item'] or any registry
        # see https://minecraft.wiki/w/Tag#List_of_tags
        self.set_json(name, json, 'tags/' + tag_type)
    

GLOBALS = Globals()

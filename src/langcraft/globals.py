from typing import Optional, Callable
import random
import string

from .serialize import Program
from .json_utils import *

DATAPACK_ROOT: str = '$root'

class Globals:
    def __init__(self, namespace='main'):
        self.debug = True
        self.namespace: str = namespace
        self.path: List[str] = []
        self.programs: Dict[str, Program] = {self.get_function_path(): Program()}
        self.structures: Dict[str] # TODO
        self.jsons: Dict[str, JSON] = {}

        self.fun = None  # : Optional[Fun]  # UNUSED, can delete
        self.blocks = []

        self.ref_graph = {}
        self.fun_hooks = {}
        self.resource_hooks = {} # TODO
    
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

    def gen_name(self) -> str:
        for i in range(1, 256):
            candidate_name = 'x' + hex(i)[2:]
            if self.get_function_path(path=[*self.path, candidate_name]) not in self.programs:
                return candidate_name

        for i in range(8, 32): # 32 == len(uuid4().hex)
            candidate_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(i)) #uuid4().hex[:i]
            if self.get_function_path(path=[*self.path, candidate_name]) not in self.programs:
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

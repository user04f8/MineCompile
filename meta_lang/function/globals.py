from typing import List, Dict, Optional
from uuid import uuid4
import random
import string

from .serialize import Program

DATAPACK_ROOT: str = '$root'

class Globals:
    def __init__(self, namespace='main'):
        self.debug = True
        self.namespace: str = namespace
        self.path: List[str] = []
        # self.path_tree: Dict[str, Dict] = {self.namespace: {}}
        self.programs: Dict[str, Program] = {self.get_full_path(): Program()}
        self.fun = None  # : Optional[Fun]  # UNUSED, can delete
        self.blocks = []

        self.ref_graph = {}
        self.fun_hooks = {}
        self.resource_hooks = {} # TODO
    
    def get_full_path(self, namespace=None, path=None):
        if namespace is None:
            namespace = self.namespace
        if path is None:
            path = self.path
        return '/'.join([DATAPACK_ROOT, namespace, 'function'] + path)

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
            assert exited_path == name, 'Path entered does not match path exited'
        self.add_current_path()

    def add_current_path(self):
        if self.get_full_path() not in self.programs:
            self.programs[self.get_full_path()] = Program()

    def gen_name(self) -> str:
        for i in range(1, 32): # 32 == len(uuid4().hex)
            candidate_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(i)) #uuid4().hex[:i]
            if self.get_full_path(path=[*self.path, candidate_name]) not in self.programs:
                return candidate_name
        assert False, 'Ran out of potential candidate names (candidate UUIDs not unique)'

    def add_statement(self, statement):
        if self.blocks == []:
            idx = len(self.programs[self.get_full_path()])
            self.programs[self.get_full_path()].append(statement)
            return (self.get_full_path(), idx)
        else:
            self.blocks[-1].add_statement(statement)
            return None

    def clear_cmd(self, pathed_idx):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = None

    def set_cmd(self, pathed_idx, cmd):
        full_path, idx = pathed_idx
        self.programs[full_path][idx] = cmd

GLOBALS = Globals()

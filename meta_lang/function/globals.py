from typing import List, Dict, Optional
from uuid import uuid4

from .serialize import Program

DATAPACK_ROOT: str = '%DATAPACK_ROOT%'

class Globals:
    def __init__(self, namespace='main'):
        self.debug = True
        self.namespace: str = namespace
        self.path: List[str] = []
        # self.path_tree: Dict[str, Dict] = {self.namespace: {}}
        self.programs: Dict[str, Program] = {self.get_full_path(): Program()}
        self.fun = None  # : Optional[Fun]
    
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
            candidate_name = uuid4().hex[:i]
            if self.get_full_path(path=[*self.path, candidate_name]) not in self.programs:
                return candidate_name
        assert False, 'Ran out of potential candidate names (candidate UUIDs not unique)'

        
    def add_cmd(self, cmd):
        # print(f'adding {repr(cmd)}')
        # print(f'    cmds:   {repr(cmd.get_cmds())}')
        # print(f'    tokens: {repr(cmd.tokenize())}')
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

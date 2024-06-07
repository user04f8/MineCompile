from typing import List, Dict

from .serialize import Program

DATAPACK_ROOT: str = '%DATAPACK_ROOT%'

class Globals:
    def __init__(self, namespace='main'):
        self.debug = True
        self.namespace: str = namespace
        self.path: List[str] = []
        self.programs: Dict[str, Program] = {self.get_full_path(): Program()}
    
    def get_full_path(self):
        return '/'.join([DATAPACK_ROOT, self.namespace, 'function'] + self.path)

    def add_current_path(self):
        if self.get_full_path() not in self.programs:
            self.programs[self.get_full_path()] = Program()
        
    def add_cmd(self, cmd):
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

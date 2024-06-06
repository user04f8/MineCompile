from typing import Dict

from .base import GLOBALS, Program, compile_all

def display_all(programs: Dict[str, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data'):
    compiled = compile_all(programs, root_dir, debug=True)
    for file_path, serialized_file in compiled.items():
        print(file_path)
        print(serialized_file)

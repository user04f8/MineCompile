from typing import Dict

from pathlib import Path
from termcolor import colored

from .base import Program, compile_all
from .globals import GLOBALS

def display_all(programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data'):
    compiled = compile_all(programs, root_dir, debug=True)
    for file_path, serialized_file in compiled.items():
        print(colored(file_path, 'light_blue', attrs=['bold', 'underline']))
        print(serialized_file)
        print()


p = Path('./data')

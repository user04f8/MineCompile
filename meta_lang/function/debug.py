from typing import Dict

from pathlib import Path
from termcolor import colored

from .base import Program, compile_all
from .globals import GLOBALS

def display_all(programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', debug=True, color=True):
    compiled = compile_all(programs, root_dir, debug=debug, color=color)
    for file_path, serialized_file in compiled.items():
        
        root, namespace, folder, *path = file_path.split('/')

        if color:
            if folder == 'function':
                print(colored(namespace + ':' + '/'.join(path), 'light_cyan', attrs=['bold', 'underline']))
            else:
                print(colored(file_path, 'blue', attrs=['bold', 'underline']))
        else:
            print(file_path, end='')
        print('\n'.join('  ' + s for s in serialized_file.split('\n')))
        print()


p = Path('./data')

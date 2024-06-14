from typing import Dict

from pathlib import Path
from termcolor import colored

from .base import Program
from .compile import compile_all
from .globals import GLOBALS

def display_all(programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', debug=True, color=True, max_optim_steps=20):
    compiled = compile_all(programs, root_dir, debug=debug, color=color, max_optim_steps=max_optim_steps)
    for file_path, serialized_file in compiled.items():
        
        root, namespace, *path = file_path.split('/')

        if color:
            match path:
                case ['function', *path]:
                    print(colored(namespace + ':' + '/'.join(path), 'light_cyan', attrs=['bold', 'underline']))
                case ['tags', 'function', *path]:
                    print(colored('#' + namespace + ':' + '/'.join(path), 'cyan', attrs=['bold', 'underline']))
                case ['tags', *path]:
                    print(colored('#' + namespace + ':' + '/'.join(path), 'cyan', attrs=['bold', 'underline']))
                case _:
                    print(colored(file_path, 'blue', attrs=['bold', 'underline']))
        else:
            print(file_path, end='')
        print('\n'.join('  ' + s for s in serialized_file.split('\n')))
        print()


p = Path('./data')

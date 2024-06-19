from copy import copy
from typing import Dict, Optional
import re
from pathlib import Path
from termcolor import colored

from .base import Program
from .compile import compile_all
from .globals import GLOBALS, DATAPACK_ROOT

def display(compiled: Dict[str, str], ident: Optional[str] = None, include_subs=True, regex: Optional[str] = None, cmd_regex: Optional[str] = None):
    
    displayed = copy(compiled)
    if regex:
        displayed = {key: val for key, val in compiled.items() if re.search(regex, key) or re.search(regex, val)}
    if cmd_regex:
        displayed = {key: val for key, val in compiled.items() if re.search(cmd_regex, val)}

    if ident:
        namespaced_ident = ident.split(':')
        if len(namespaced_ident) == 2:
            namespace, path = namespaced_ident
            ident = GLOBALS.get_function_path(namespace, path.split('/'))
        if include_subs:
            displayed = {full_ident: compiled[full_ident] for full_ident in compiled if ident in full_ident}
        else:
            displayed = {ident: compiled[ident]}
    display_all(displayed)


def display_all(compiled=None, programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', debug=True, color=True, optim=True):
    if compiled is None:
        compiled = compile_all(programs, root_dir, debug=debug, color=color, optim=optim)
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
        print('\n'.join(s for s in serialized_file.split('\n')))
        print()


p = Path('./data')

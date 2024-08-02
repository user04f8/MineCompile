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


def display_all(compiled=None, programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', debug=True, color=True, optim=True, print=print):
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
            print(file_path)
        print('\n'.join(s for s in serialized_file.split('\n')))
        print()

def display_diff(compiled_a: Dict[str, str], compiled_b: Dict[str, str], width: int = 150, sep='| ', full=False, print=print):
    captured = [[], []]
    def capture_print(idx):
        def inner(obj=''):
            captured[idx].append(obj)
        return inner

    def wrap(s: str, width: int, indent='  '):
        def wrap_inner(s: str, width_inner: int):
            if len(s) <= width_inner:
                return s + ' ' * (width_inner - len(s))
            else:
                return s[:width_inner-3] + f'...\n{indent}' + wrap_inner(s[width_inner-3:], width - len(indent))
        
        lines = s.split('\n')
        out = []
        for line in lines:
            out.append(wrap_inner(line, width))
        
        return '\n'.join(out)

    def columns(s0: str, s1: str):
        lines0, lines1 = s0.split('\n'), s1.split('\n')
        lines0 += [None] * (len(lines1) - len(lines0))
        lines1 += [None] * (len(lines0) - len(lines1))
        out = []
        for line0, line1 in zip(lines0, lines1):
            out.append(line0 + sep + line1)
        return '\n'.join(out)
    
    display_all(compiled_a, print=capture_print(0), color=False)
    display_all(compiled_b, print=capture_print(1), color=False)

    if full:
        out = columns(*(wrap('\n'.join(captured_i), (width-len(sep))//2) for captured_i in captured))
        print(out)
    else:
        i = j = 0
        while i < len(captured[0]) or j < len(captured[1]):
            pass #TODO

p = Path('./data')

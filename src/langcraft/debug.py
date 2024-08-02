from copy import copy
from typing import Dict, Optional
import re
from pathlib import Path
from termcolor import colored
from difflib import unified_diff

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

def display_colored_path(file_path, overwrite_color=None, print=print):
    if file_path == '$hash':
        print(colored('$hash', 'yellow', attrs=['bold']))
    else:
        root, namespace, *path = file_path.split('/')
        match path:
            case ['function', *path]:
                print(colored(namespace + ':' + '/'.join(path), (overwrite_color if overwrite_color else 'light_cyan'), attrs=['bold', 'underline']))
            case ['tags', 'function', *path]:
                print(colored('#' + namespace + ':' + '/'.join(path), (overwrite_color if overwrite_color else 'cyan'), attrs=['bold', 'underline']))
            case ['tags', *path]:
                print(colored('#' + namespace + ':' + '/'.join(path), (overwrite_color if overwrite_color else 'cyan'), attrs=['bold', 'underline']))
            case _:
                print(colored(file_path, (overwrite_color if overwrite_color else 'blue'), attrs=['bold', 'underline']))

def display_all(compiled=None, programs: Dict[Path, Program] = GLOBALS.programs, root_dir: str = './datapacks/testing/data', debug=True, color=True, optim=True, print=print):
    if compiled is None:
        compiled = compile_all(programs, root_dir, debug=debug, color=color, optim=optim)
    for file_path, serialized_file in compiled.items():
        if color:
            display_colored_path(file_path, print=print)
        else:
            print(file_path)
        print('\n'.join(s for s in serialized_file.split('\n')))
        print()

def display_diff(compiled_a: Dict[str, str], compiled_b: Dict[str, str], width: int = 150, sep='| ', simple=False):
    captured = [[], []]
    def capture_print(idx):
        def inner(obj=''):
            captured[idx].append(obj)
        return inner
    
    class ColoredStr(str):
        def color(self, color, color_idx=None):
            self._color = color
            self._color_idx = color_idx
            return self

        def apply_color(self) -> str:
            if self._color_idx:
                i, j = self._color_idx
                return self[:i] + colored(self[i:j], self._color) + self[j:]
            else:
                return colored(self, self._color)
            
        def __add__(self, s):
            return ColoredStr(super().__add__(s)).color(self._color, color_idx=self._color_idx)
        
        def __radd__(self, s):
            return ColoredStr(super().__radd__(s)).color(self._color, color_idx=len(s) + self._color_idx)

    def wrap(lines: list[str | ColoredStr], width: int, indent='  '):
        def wrap_inner(s: str, width_inner: int):
            if len(s) <= width_inner:
                return s + ' ' * (width_inner - len(s))
            else:
                # if s.find('\x1b') == -1:
                return s[:width_inner-3] + f'...\n{indent}' + wrap_inner(s[width_inner-3:], width - len(indent))
                # else:
                #     return s[:width_inner+5-3] + f'\x1b[m...\n{indent}' + s[:5] + wrap_inner(s[width_inner+5-3:], width - len(indent))

        out = []
        for line in lines:
            wrapped_line = wrap_inner(line, width)
            if isinstance(wrapped_line, ColoredStr):
                wrapped_line = wrapped_line.apply_color()
            out.append(wrapped_line)
        
        return '\n'.join(out)

    def columns(s0: str, s1: str):
        lines0, lines1 = s0.split('\n'), s1.split('\n')
        lines0 += [''] * (len(lines1) - len(lines0))
        lines1 += [''] * (len(lines0) - len(lines1))
        out = []
        for line0, line1 in zip(lines0, lines1):
            out.append(line0 + sep + line1)
        return '\n'.join(out)
    
    half_width = (width-len(sep))//2
    if simple:
        display_all(compiled_a, print=capture_print(0), color=False)
        display_all(compiled_b, print=capture_print(1), color=False)
        out = columns(*(wrap(captured_i, half_width) for captured_i in captured))
        print(out)
    else:
        
        for file_path, serialized_file_a in compiled_a.items():
            if file_path not in compiled_b:
                display_colored_path(file_path, overwrite_color='red', print=print)
                for line in serialized_file_a.split('\n'):
                    print(colored(line, 'red'))
            else:
                serialized_file_b = compiled_b[file_path]
                if serialized_file_a == serialized_file_b:
                    continue
                
                display_colored_path(file_path, print=print)
                i = j = 0
                lines_a, lines_b = serialized_file_a.split('\n'), serialized_file_b.split('\n')
                column_a, column_b = [], []
                MAX_N = min(99, max(len(lines_a), len(lines_b)))
                while i < len(lines_a) and j < len(lines_b):
                    n = 1
                    while lines_a[i] != lines_b[j] and n <= MAX_N:
                        for k in range(n + 1):
                            i_, j_ = i + n - k, j + k
                            if i_ >= len(lines_a) or j_ >= len(lines_b):
                                continue
                            if lines_a[i_] == lines_b[j_]:
                                if (i_ - i) == (j_ - j):
                                    while i < i_:
                                        column_a.append(ColoredStr(lines_a[i]).color('red'))
                                        column_b.append(ColoredStr(lines_b[j]).color('green'))
                                        i += 1
                                        j += 1
                                else:
                                    while i < i_:
                                        column_a.append(ColoredStr(lines_a[i]).color('red'))
                                        column_b.append('---')
                                        i += 1
                                    while j < j_:
                                        column_a.append('---')
                                        column_b.append(ColoredStr(lines_b[j]).color('green'))
                                        j += 1
                                break
                        n += 1
                    if n > MAX_N:
                        column_a.append(ColoredStr(lines_a[i]).color('red'))
                        column_b.append(ColoredStr(lines_b[j]).color('green'))
                    else:
                        column_a.append(lines_a[i])
                        column_b.append(lines_b[j])
                    i += 1
                    j += 1
                while i < len(lines_a):
                    column_a.append(ColoredStr(lines_a[i]).color('red'))
                    column_b.append('---')
                    i += 1
                while j < len(lines_b):
                    column_a.append('---')
                    column_b.append(ColoredStr(lines_b[j]).color('green'))
                    j += 1

                print(columns(wrap(column_a, half_width), wrap(column_b, half_width)))
                    
        for file_path, serialized_file_b in compiled_b.items():
            if file_path not in compiled_a:
                display_colored_path(file_path, overwrite_color='green', print=print)
                for line in serialized_file_b.split('\n'):
                    print(colored(line, 'green'))

        # diff = list(unified_diff(captured[0], captured[1]))
        
        # print('\n'.join(diff))
        # i = j = 0
        # while i < len(captured[0]) or j < len(captured[1]):
        #     pass #TODO

p = Path('./data')

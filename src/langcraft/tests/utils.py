from inspect import getsource
from hashlib import sha256
import json
from pathlib import Path
from termcolor import cprint

from langcraft import compile_all, display_all, GLOBALS
from langcraft.debug import display_diff

tests = []

def test(name: str):
    def wrapper(funct):
        def inner():
            GLOBALS.reset('test')

            funct()
            out = compile_all()

            funct_hash = sha256(getsource(funct).encode()).hexdigest()
            

            path = Path(name.replace('langcraft.tests.', 'langcraft/tests/') + '_' + funct.__name__ + '.json')

            if path.exists():
                with path.open() as f:
                    validation = json.load(f)
                    if validation['$hash'] == funct_hash:
                        if out != validation:
                            cprint("!!!!!!!!!!!!!!", 'red', attrs=['reverse', 'blink', 'bold'])
                            cprint("!Test failure!", 'red', attrs=['reverse', 'blink', 'bold'])
                            cprint("!!!!!!!!!!!!!!", 'red', attrs=['reverse', 'blink', 'bold'])
                            del validation['$hash']
                            display_diff(validation, out)

                    else:
                        out['$hash'] = funct_hash
                        json.dump(out, f)
            else:
                with path.open('w') as f:
                    out['$hash'] = funct_hash
                    json.dump(out, f)
            if '$hash' in out:
                del out['$hash']
            # display_all(out)
        tests.append(inner)
    return wrapper
    # return lambda: None



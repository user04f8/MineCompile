from __future__ import annotations

class Code(str):
    def __add__(self, other):
        if isinstance(other, Code) or isinstance(other, str):
            return Code(super().__add__(other))
        else:
            return Code(super().__add__(repr(other)))
    
    def __mul__(self, other: int):
        if isinstance(other, int):
            return Code(super().__mul__(other))
        else:
            raise TypeError(f'Unsupported opperand type for *: Code and {type(other)}')
    
    def __rmul__(self, other: int):
        if isinstance(other, int):
            return Code(super().__mul__(other))
        else:
            raise TypeError(f'Unsupported opperand type for *: {type(other)} and Code')

    def __repr__(self):
        return f'Code({super().__repr__()})'

class CodeHook:
    def __init__(self, ident):
        self.ident = ident
    
    def __repr__(self):
        return f'${self.ident}'

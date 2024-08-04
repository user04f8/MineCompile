import ply.lex as lex
from ply.lex import TOKEN

class Lexer:
    tokens = ('NUMBER', 'IDENT')

    def __init__(self):
        self.lineno = 0
        self.build()

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)

    def input(self, program):
        self.lexer.input(program)

    def __iter__(self):
        return iter(self.lexer)

    @TOKEN(r'a+')
    def t_IDENT(self, t):
        t.value = int(t.value)
        return t
    
    @TOKEN(r'\d+')
    def t_NUMBER(self, t):
        t.value = int(t.value)
        return t
    
    @TOKEN(r'\n+')
    def t_newline(self, t):
        pass
    
    t_ignore  = ' \t'

lexer = Lexer()

# Test the lexer
data = '''
1 2 4 5 6
'''
lexer.input(data)

# Tokenize
for tok in lexer:
    print(tok)
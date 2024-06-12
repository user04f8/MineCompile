### base.py

class Alias(EmptyStatement):
    def __init__(self, kw, kw_replace):
        self.kw: Token = kw
        self.kw_replace: Token = kw_replace

    def _apply_token(self, token: Token):
        if self.kw == token:
            return self.kw_replace

    def apply(self, cmd: TokensContainer):
        return TokensContainer(*(self._apply_token(token) for token in cmd))
        
# class ArgAliases(Alias):
#     def __init__(self, *args):
#         self.args = args
#         self.kw = self.default()

#     @staticmethod
#     def default(i):
#         return VarToken(Selector(), f'_{i}')
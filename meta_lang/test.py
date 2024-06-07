from function import *

with Pathspace('test'):
    Advancement.grant(Selector(), ResourceLocation('kjsakflj'))
    Statement('# comment here')
    If('block ~ ~ ~ air') (
        Statement('do thing')
    ).Else(
        Statement('nevermind')
    )
    Statement([TokensContainer(StrToken('# comment'), ChoiceSpecialToken(Selector(), Selector('a')))])

    

display_all()
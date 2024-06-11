from function import *

with Fun('f') as f:
    with While('block ~ ~ ~ air'):
        Statement('say hi')

with Fun('g')[int] as (g, x):
    Statement(x)

with TickingFun():
    f()
    Statement('the quick brown fox jumps over the lazy dog')
    with If(Condition('A') & (Condition('B') | Condition('D'))):
        g('test')
    
    Advancement.grant(Selector(), ResourceLocation('main:loc'))

display_all()
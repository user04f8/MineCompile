from langcraft import *



with Partial(Fun) as (f, args):
    selector, advancement = args(2)
    Advancement.grant(selector, advancement)
    # Statement(x)
    # Statement(y)

with TickingFun():
    
    f(_SelectorType(), ResourceLocation('minecraft:asdfjkl'))()

    with Fun()[int, int] as (g, (x, y)):
        Statement(x)
        Statement(y)

    g()

print(g.in_types)
print(g.out_types)


display_all()
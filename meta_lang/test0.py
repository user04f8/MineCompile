from function import *


# with Fun() as f:
#     Statement('test')

with PublicFun('main') as main:
    with Fun('f') as f:
            If('block ~ ~ ~ air') (
                Statement('tp ^ ^ ^1'),
                f()
            )
    f()

    If(Condition('condition')) (
          Statement('say hi'),
          Statement('say bye')
    )
    with While('block ~ ~ ~ air'):
        Statement('tp ^ ^ ^1')
        Statement('tp ~ ~ ~')
    
    # with If('block ~ ~ ~ air'):
    #     Advancement.grant(Choice(Selector(), Selector('n')), '*')


# with Pathspace('test'):
#     Advancement.grant(Selector(), ResourceLocation('kjsakflj'))
#     Statement('# comment here')
#     If('block ~ ~ ~ air') (
#         Statement('do thing')
#     ).Else(
#         Statement('nevermind')
#     )
#     Statement([TokensContainer(StrToken('# comment'), ChoiceSpecialToken(Selector(), Selector('a')))])

#     While (Condition('a')) (
#         Statement('asdfjkl')
#     )

#    IDEA not current syntax:
# with Pathspace('control_flow'):
#     with Fun()[Condition, Block] as (while_, (c, b)):
#         c: Condition
#         b: Block
#         If(c) (
#             *b,
#             while_(c, b)
#         )

# def custom_while(c: Condition, b: Block):
#     with Fun() as f:
#         If(c) (
#             *b.statements,
#             f()
#         )

# custom_while(
#     Condition('block ~ ~ ~ air'),
#     Block(
#         Statement('tp @s ^ ^ ^1')
#     )
# )

if __name__ == '__main__':
    display_all()
from function import *

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

def while_(c: Condition, b: Block):
    with Fun() as f:
        If(c) (
            *b.statements,
            f()
        )

while_(
    Condition('block ~ ~ ~ air'),
    Block(
        Statement('tp @s ^ ^ ^1')
    )
)

display_all()
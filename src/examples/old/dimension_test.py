from langcraft import *
legacy_init('dimensions')

dim = CustomDimension.noise(
    'floating_islands',
    type_= 'overworld',
    preset='minecraft:floating_islands'
)

CustomDimension.noise(
    'jagged',
    type_='overworld',
    preset='minecraft:overworld',
    biome_source=JSON(
        type='fixed',
        biome='jagged_peaks'
    )
)

@public
def to_floating_islands():
    with SelfEntity().in_(dim) as s:
        s.teleport()

@public
def to_debug():
    with SelfEntity().in_(CustomDimension(name='asdfjkl',type_='overworld',generator_type='debug')) as s:
        s.teleport()

display_all()
compile_all(write=True, root_dir='../datapacks/dimensions')
tp @s ~ 330 ~

clear
effect clear @s
effect give @s minecraft:instant_health 5 10
effect give @s minecraft:resistance 5 10
effect give @s minecraft:absorption 5 10
effect give @s minecraft:saturation 15 10
effect give @s minecraft:slow_falling 5 10
fill ~-30 300 ~-30 ~30 300 ~30 white_wool
fill ~-30 299 ~-30 ~30 299 ~30 light_gray_wool
fill ~-30 298 ~-30 ~30 298 ~30 gray_wool
fill ~-30 297 ~-30 ~30 297 ~30 black_wool

summon pillager ~-5 303 ~20
summon pillager ~-4 303 ~20
summon zombie ~-3 303 ~20
summon pillager ~-2 303 ~20
summon pillager ~-1 303 ~20
summon skeleton ~5 303 ~20
summon pillager ~4 303 ~20
summon creeper ~3 303 ~20
summon pillager ~2 303 ~20
summon pillager ~1 303 ~20
summon pillager ~ 303 ~20
summon pillager ~-5 303 ~18
summon creeper ~-4 303 ~18
summon skeletno ~-3 303 ~18
summon pillager ~-2 303 ~18
summon pillager ~-1 303 ~18
summon pillager ~5 303 ~18
summon zombie ~4 303 ~18
summon pillager ~3 303 ~18
summon skeleton ~2 303 ~18
summon pillager ~1 303 ~18
summon pillager ~ 303 ~18
enchant @e[type=minecraft:pillager, distance=..40] testing:explode 5
enchant @e[type=minecraft:skeleton, distance=..40] testing:shuriken 5
effect give @e[type=minecraft:pillager, distance=..40] speed infinite
effect give @e[type=minecraft:pillager, distance=..40] resistance infinite
effect give @e[type=minecraft:pillager, distance=..40] slow_falling 10
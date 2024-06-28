# requires track_elements

function main:triple_helix

summon skeleton ~ ~15 ~4
summon skeleton ~2 ~15 ~2
summon skeleton ~4 ~15 ~
summon skeleton ~2 ~15 ~-2
summon skeleton ~ ~15 ~-4
summon skeleton ~-2 ~15 ~-2
summon skeleton ~-4 ~15 ~
summon skeleton ~-2 ~15 ~2

enchant @e[type=minecraft:skeleton] power 5
enchant @e[type=minecraft:skeleton] punch 2
enchant @e[type=minecraft:skeleton] flame

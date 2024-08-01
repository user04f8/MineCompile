from typing import Literal

_Mobs = Literal[
    'allay',
    'armadillo',
    'armor_stand',
    'axolotl',
    'bat',
    'bee',
    'blaze',
    'breeze',
    'camel',
    'cat',
    'cave_spider',
    'chicken',
    'cod',
    'cow',
    'creeper',
    'dolphin',
    'donkey',
    'drowned',
    'elder_guardian',
    'ender_dragon',
    'enderman',
    'endermite',
    'evoker',
    'fox',
    'frog',
    'ghast',
    'giant',
    'glow_squid',
    'goat',
    'guardian',
    'hoglin',
    'horse',
    'husk',
    'illusioner',
    'iron_golem',
    'llama',
    'magma_cube',
    'mooshroom',
    'mule',
    'ocelot',
    'panda',
    'parrot',
    'phantom',
    'pig',
    'piglin',
    'piglin_brute',
    'pillager',
    'player',
    'polar_bear',
    'pufferfish',
    'rabbit',
    'ravager',
    'salmon',
    'sheep',
    'shulker',
    'silverfish',
    'sniffer',
    'skeleton',
    'skeleton_horse',
    'slime',
    'snow_golem',
    'spider',
    'squid',
    'stray',
    'strider',
    'tadpole',
    'trader_llama',
    'tropical_fish',
    'turtle',
    'vex',
    'villager',
    'vindicator',
    'wandering_trader',
    'warden',
    'witch',
    'wither',
    'wither_skeleton',
    'wolf',
    'zoglin',
    'zombie',
    'zombie_horse',
    'zombie_villager',
    'zombified_piglin',
]

_ProjectileEntities = Literal['arrow', 'dragon_fireball', 'egg', 'ender_pearl', 'experience_bottle', 'eye_of_ender', 'fireball', 'firework_rocket', 'llama_spit', 'potion', 'shulker_bullet', 'small_fireball', 'snowball', 'spectral_arrow', 'trident', 'wither_skull']

_VehicleEntities = Literal['boat', 'chest_boat', 'chest_minecart', 'command_block_minecart', 'furnace_minecart', 'hopper_minecart', 'minecart', 'spawner_minecart', 'tnt_minecart']

_BlockEntities = Literal['falling_block', 'tnt']

_MiscEntities = Literal['area_effect_cloud', 'end_crystal', 'evoker_fangs', 'fishing_bobber', 'glow_item_frame', 'item_frame', 'leash_knot', 'lightning_bolt', 'marker', 'interaction', 'block_display', 'item_display', 'text_display', 'painting', 'experience_orb', 'item']

type EntityType = _Mobs | _ProjectileEntities | _VehicleEntities | _BlockEntities | _MiscEntities
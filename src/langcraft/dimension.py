from typing import List, Literal, Optional

from .json_utils import JSON
from .types import Dimension, ExternalResourceLocation
from .minecraft_builtins import _BuiltinDimensionTypeLiteral, _BuiltinDimensionLiteral, _Blocks
from .globals import GLOBALS


class CustomDimensionType:
    pass

_DimensionType = _BuiltinDimensionTypeLiteral | CustomDimensionType | ExternalResourceLocation

_CustomDimension_noise_min_y_literal = Literal[-2032, -2016, -2000, -1984, -1968, -1952, -1936, -1920, -1904, -1888, -1872, -1856, -1840, -1824, -1808, -1792, -1776, -1760, -1744, -1728, -1712, -1696, -1680, -1664, -1648, -1632, -1616, -1600, -1584, -1568, -1552, -1536, -1520, -1504, -1488, -1472, -1456, -1440, -1424, -1408, -1392, -1376, -1360, -1344, -1328, -1312, -1296, -1280, -1264, -1248, -1232, -1216, -1200, -1184, -1168, -1152, -1136, -1120, -1104, -1088, -1072, -1056, -1040, -1024, -1008, -992, -976, -960, -944, -928, -912, -896, -880, -864, -848, -832, -816, -800, -784, -768, -752, -736, -720, -704, -688, -672, -656, -640, -624, -608, -592, -576, -560, -544, -528, -512, -496, -480, -464, -448, -432, -416, -400, -384, -368, -352, -336, -320, -304, -288, -272, -256, -240, -224, -208, -192, -176, -160, -144, -128, -112, -96, -80, -64, -48, -32, -16, 0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256, 272, 288, 304, 320, 336, 352, 368, 384, 400, 416, 432, 448, 464, 480, 496, 512, 528, 544, 560, 576, 592, 608, 624, 640, 656, 672, 688, 704, 720, 736, 752, 768, 784, 800, 816, 832, 848, 864, 880, 896, 912, 928, 944, 960, 976, 992, 1008, 1024, 1040, 1056, 1072, 1088, 1104, 1120, 1136, 1152, 1168, 1184, 1200, 1216, 1232, 1248, 1264, 1280, 1296, 1312, 1328, 1344, 1360, 1376, 1392, 1408, 1424, 1440, 1456, 1472, 1488, 1504, 1520, 1536, 1552, 1568, 1584, 1600, 1616, 1632, 1648, 1664, 1680, 1696, 1712, 1728, 1744, 1760, 1776, 1792, 1808, 1824, 1840, 1856, 1872, 1888, 1904, 1920, 1936, 1952, 1968, 1984, 2000, 2016]
_CustomDimension_noise_height_literal = Literal[0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256, 272, 288, 304, 320, 336, 352, 368, 384, 400, 416, 432, 448, 464, 480, 496, 512, 528, 544, 560, 576, 592, 608, 624, 640, 656, 672, 688, 704, 720, 736, 752, 768, 784, 800, 816, 832, 848, 864, 880, 896, 912, 928, 944, 960, 976, 992, 1008, 1024, 1040, 1056, 1072, 1088, 1104, 1120, 1136, 1152, 1168, 1184, 1200, 1216, 1232, 1248, 1264, 1280, 1296, 1312, 1328, 1344, 1360, 1376, 1392, 1408, 1424, 1440, 1456, 1472, 1488, 1504, 1520, 1536, 1552, 1568, 1584, 1600, 1616, 1632, 1648, 1664, 1680, 1696, 1712, 1728, 1744, 1760, 1776, 1792, 1808, 1824, 1840, 1856, 1872, 1888, 1904, 1920, 1936, 1952, 1968, 1984, 2000, 2016, 2032, 2048, 2064, 2080, 2096, 2112, 2128, 2144, 2160, 2176, 2192, 2208, 2224, 2240, 2256, 2272, 2288, 2304, 2320, 2336, 2352, 2368, 2384, 2400, 2416, 2432, 2448, 2464, 2480, 2496, 2512, 2528, 2544, 2560, 2576, 2592, 2608, 2624, 2640, 2656, 2672, 2688, 2704, 2720, 2736, 2752, 2768, 2784, 2800, 2816, 2832, 2848, 2864, 2880, 2896, 2912, 2928, 2944, 2960, 2976, 2992, 3008, 3024, 3040, 3056, 3072, 3088, 3104, 3120, 3136, 3152, 3168, 3184, 3200, 3216, 3232, 3248, 3264, 3280, 3296, 3312, 3328, 3344, 3360, 3376, 3392, 3408, 3424, 3440, 3456, 3472, 3488, 3504, 3520, 3536, 3552, 3568, 3584, 3600, 3616, 3632, 3648, 3664, 3680, 3696, 3712, 3728, 3744, 3760, 3776, 3792, 3808, 3824, 3840, 3856, 3872, 3888, 3904, 3920, 3936, 3952, 3968, 3984, 4000, 4016, 4032, 4048, 4064]

class CustomDimension:
    def __init__(self,
                 name: str,
                 type_: _DimensionType,
                 generator_type: Literal['noise', 'flat', 'debug'],
                 settings=None,
                 biome_source=None):
        self.name = name
        self.json = JSON(
            type=str(type_),
            generator=JSON(
                type=generator_type,
                **({"settings": settings} if settings is not None else {}),
                **({"biome_source": biome_source} if biome_source is not None else {})
            )
        )

        GLOBALS.add_json('dimension', self.name, self.json)
    
    @classmethod
    def noise(cls,
              name: str,
              type_: _DimensionType,
              preset: Optional[Literal['minecraft:overworld', 'minecraft:amplified', 'minecraft:nether', 'minecraft:caves', 'minecraft:end', 'minecraft:floating_islands']] = None,
              # settings
              sea_level: int = 64,
              disable_mob_generation: bool = False,
              ore_veins_enabled: bool = True,
              aquifers_enabled: bool = True,
              legacy_random_source: bool = False,
              default_block: _Blocks = 'stone',
              default_block_properties: JSON = JSON(),
              default_fluid: _Blocks = 'water',
              default_fluid_properties: JSON = JSON(),
              spawn_target: List[JSON] = [],
              # settings.noise
              noise_min_y: _CustomDimension_noise_min_y_literal = 32,
              noise_height: _CustomDimension_noise_height_literal = 64,
              noise_size_horizontal: Literal[0, 1, 2, 3, 4] = 2,
              noise_size_vertical: Literal[0, 1, 2, 3, 4] = 2,
              noise_router: JSON = JSON(),  # https://minecraft.wiki/w/Noise_router
              surface_rule: JSON = JSON(),  # https://minecraft.wiki/w/Surface_rule
              # biome_source
              biome_source: JSON = JSON(),
            #   biome_source_type: Literal['checkerboard', 'fixed', 'multi_noise', 'the_end'] = 'multi_noise',
            #   biome_source_kwargs: dict = {'preset': 'overworld'} # https://minecraft.wiki/w/Dimension_definition#Biome_sources
              ):
        if preset:
            cls(
                name=name,
                type_=type_,
                generator_type='noise',
                settings=preset,
                biome_source=biome_source
            )
        else:
            cls(
                name=name,
                type_=type_,
                generator_type='noise',
                settings=JSON(
                    sea_level=sea_level,
                    disable_mob_generation=disable_mob_generation,
                    ore_veins_enabled=ore_veins_enabled,
                    aquifers_enabled=aquifers_enabled,
                    legacy_random_source=legacy_random_source,
                    default_block=JSON(
                        Name=default_block,
                        Properties=default_block_properties
                    ),
                    default_fluid=JSON(
                        Name=default_fluid,
                        Properties=default_fluid_properties
                    ),
                    spawn_target=spawn_target,
                    noise=JSON(
                        min_y=noise_min_y,
                        height=noise_height,
                        size_horizontal=noise_size_horizontal,
                        size_vertical=noise_size_vertical
                    ),
                    noise_router=noise_router,
                    surface_rule=surface_rule
                ),
                biome_source=biome_source 
                # JSON(
                #     type=biome_source_type,
                #     **biome_source_kwargs
                # )
            )

_Dimension = _BuiltinDimensionLiteral | CustomDimension | Dimension

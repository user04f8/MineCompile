from enum import StrEnum
import json
from typing import Union, List, Optional, Dict, Literal, Self
from termcolor import colored

from .globals import GLOBALS
from .debug_utils import print_debug
from .serialize import ResourceLocToken, TokenBase, SelectorToken, Serializable
from .minecraft_builtins import _BuiltinDimensionLiteral, EntityType

class JSONText(Serializable):
    def __init__(self, 
                 text: Union[str, List[Union[str, Dict]]] = None,
                 extra: Optional[List[Union[str, Dict]]] = None,
                 type: Optional[Literal['text', 'translatable', 'score', 'selector', 'keybind', 'nbt']] = None,
                 color: Optional[str] = None,
                 font: Optional[str] = None,
                 bold: Optional[bool] = None,
                 italic: Optional[bool] = None,
                 underlined: Optional[bool] = None,
                 strikethrough: Optional[bool] = None,
                 obfuscated: Optional[bool] = None,
                 insertion: Optional[str] = None,
                 click_event: Optional[Dict[Literal['action', 'value'], str]] = None,
                 hover_event: Optional[Dict[Literal['action', 'contents'], str | dict | Self]] = None,
                 components: Optional[List[Self]] = None,
                 translate: Optional[str] = None,
                 fallback: Optional[str] = None,
                 with_: Optional[List[Union[str, Dict]]] = None,
                 selector: Optional[str] = None,
                 separator: Optional[Dict] = None,
                 score_name: Optional[str] = None,
                 score_objective: Optional[str] = None,
                 keybind: Optional[str] = None,
                 nbt: Optional[str] = None,
                 source: Optional[Literal['block', 'entity', 'storage']] = None,
                 interpret: Optional[bool] = None,
                 block: Optional[str] = None,
                 entity: Optional[str] = None,
                 storage: Optional[str] = None):
        
        self.text = text
        self.extra = extra
        self.type = type
        self.color = color
        self.font = font
        self.bold = bold
        self.italic = italic
        self.underlined = underlined
        self.strikethrough = strikethrough
        self.obfuscated = obfuscated
        self.insertion = insertion
        self.click_event = click_event
        self.hover_event = hover_event
        self.components = components or []

        # Content-specific attributes
        self.translate = translate
        self.fallback = fallback
        self.with_ = with_
        self.selector = selector
        self.separator = separator
        self.score_name = score_name
        self.score_objective = score_objective
        self.keybind = keybind
        self.nbt = nbt
        self.source = source
        self.interpret = interpret
        self.block = block
        self.entity = entity
        self.storage = storage

    def to_dict(self):
        result = {}
        
        if isinstance(self.text, str):
            result["text"] = self.text
        elif isinstance(self.text, list):
            result["text"] = self.text[0]
            if len(self.text) > 1:
                result["extra"] = self.text[1:]
        
        if self.extra:
            result["extra"] = self.extra

        if self.type:
            result["type"] = self.type
        
        if self.color:
            result["color"] = self.color
        
        if self.font:
            result["font"] = self.font
        
        if self.bold is not None:
            result["bold"] = self.bold
        
        if self.italic is not None:
            result["italic"] = self.italic
        
        if self.underlined is not None:
            result["underlined"] = self.underlined
        
        if self.strikethrough is not None:
            result["strikethrough"] = self.strikethrough
        
        if self.obfuscated is not None:
            result["obfuscated"] = self.obfuscated
        
        if self.insertion:
            result["insertion"] = self.insertion
        
        if self.click_event:
            result["clickEvent"] = self.click_event
        
        if self.hover_event:
            result["hoverEvent"] = self.hover_event

        if self.components:
            result["extra"] = [component.to_dict() for component in self.components]

        if self.translate:
            result["translate"] = self.translate
        if self.fallback:
            result["fallback"] = self.fallback
        if self.with_:
            result["with"] = self.with_
        
        if self.selector:
            result["selector"] = self.selector
        if self.separator:
            result["separator"] = self.separator
        
        if self.score_name and self.score_objective:
            result["score"] = {"name": self.score_name, "objective": self.score_objective}
        
        if self.keybind:
            result["keybind"] = self.keybind
        
        if self.nbt:
            result["nbt"] = self.nbt
        if self.source:
            result["source"] = self.source
        if self.interpret is not None:
            result["interpret"] = self.interpret
        if self.block:
            result["block"] = self.block
        if self.entity:
            result["entity"] = self.entity
        if self.storage:
            result["storage"] = self.storage

        return result

    def __str__(self):
        # Simplification logic
        if isinstance(self.text, str):
            if not self.extra and not self.type and not self.color and not self.font and \
               not self.bold and not self.italic and not self.underlined and \
               not self.strikethrough and not self.obfuscated and not self.insertion and \
               not self.click_event and not self.hover_event and not self.components and \
               not self.translate and not self.fallback and not self.with_ and \
               not self.selector and not self.separator and not self.score_name and \
               not self.score_objective and not self.keybind and not self.nbt and \
               not self.source and not self.interpret and not self.block and \
               not self.entity and not self.storage:
                return json.dumps(self.text)
        
        if isinstance(self.text, list):
            if all(isinstance(item, str) for item in self.text) and not self.extra and \
               not self.type and not self.color and not self.font and not self.bold and \
               not self.italic and not self.underlined and not self.strikethrough and \
               not self.obfuscated and not self.insertion and not self.click_event and \
               not self.hover_event and not self.components and not self.translate and \
               not self.fallback and not self.with_ and not self.selector and not self.separator and \
               not self.score_name and not self.score_objective and not self.keybind and \
               not self.nbt and not self.source and not self.interpret and not self.block and \
               not self.entity and not self.storage:
                return json.dumps(self.text)
            
        def to_dict(json_text: Self):
            return json_text.to_dict()

        return json.dumps(self.to_dict(), ensure_ascii=False, default=to_dict)

    def __add__(self, other: Self) -> Self:
        if self.extra:
            self.extra.append(other)
        else:
            self.extra = [other]
        return self

    def debug_str(self):
        def apply_styles(text, color=None, bold=None, italic=None, underlined=None, strikethrough=None, obfuscated=None):
            attrs = []
            if bold:
                attrs.append('bold')
            if italic:
                attrs.append('italic')
            if underlined:
                text = f'\033[4m{text}\033[0m'  # Underline
            if strikethrough:
                text = f'\033[9m{text}\033[0m'  # Strikethrough
            if obfuscated:
                text = ''.join(['*' if c != ' ' else ' ' for c in text])  # Simple obfuscation
            try:
                return colored(text, color, attrs=attrs)
            except KeyError:
                return colored(text, attrs=attrs)
        
        if self.type == 'translatable':
            preview = f'Translatable: {self.translate} ({", ".join(self.with_ or [])})'
        elif self.type == 'selector':
            preview = f'Selector: {self.selector}'
        elif self.type == 'score':
            preview = f'Score: {self.score_name} ({self.score_objective})'
        elif self.type == 'keybind':
            preview = f'Keybind: {self.keybind}'
        elif self.type == 'nbt':
            preview = f'NBT: {self.nbt} (source: {self.source})'
        else:
            preview = apply_styles(
                self.text if isinstance(self.text, str) else ' '.join(self.text),
                self.color, self.bold, self.italic, self.underlined,
                self.strikethrough, self.obfuscated
            )

        if self.components:
            for component in self.components:
                preview += ' ' + component.debug_str()

        return preview

_SliceType = int | str  # str that is of form #, #.., ..#, or #..#

_SELECTOR_TYPE = Literal['s'] | Literal['a'] | Literal['p'] | Literal['e'] | Literal['n'] | Literal['r']

class _SelectorBase(Serializable):
    def __init__(self,
                 selector_type: _SELECTOR_TYPE = 's',
                 **selector_kwargs):
        selector_kwargs = {key: val for key, val in selector_kwargs.items() if val is not None}
        self.token: SelectorToken = SelectorToken(selector_type, **selector_kwargs)

    def __eq__(self, sel: Self):
        if isinstance(sel, _SelectorBase):
            return (self.token.s == sel.token.s and self.token.kwargs == sel.token.kwargs)
        else:
            return False

class _SingleSelectorBase(_SelectorBase):
    def __init__(self, s: str | _SelectorBase = 's', **kwargs) -> None:
        if isinstance(s, _SelectorBase):
            self.token = s.token
        else:
            super().__init__(s, **kwargs)
        if self.token.s not in {'p', 'r', 's', 'n'}:
            if 'limit' in self.token.kwargs and self.token.kwargs['limit'] != 1:
                raise ValueError(f"Non-singular selector token @{self.token.s} with limit={self.token.kwargs['limit']}")
            self.token.kwargs['limit'] = 1


class _PlayerSelectorBase(_SelectorBase):
    def __init__(self, s: str | _SelectorBase = 'a', **kwargs) -> None:
        if isinstance(s, _SelectorBase):
            self.token = s.token
        else:
            super().__init__(s, **kwargs)
        if self.token.s not in {'p', 'r', 's', 'a'}:
            raise ValueError(f"@{self.token.s}: not a player selector token")


class _SinglePlayerSelectorBase(_PlayerSelectorBase):
    def __init__(self, s: str | _SelectorBase = 'p', **kwargs) -> None:
        if isinstance(s, _SelectorBase):
            self.token = s.token
        else:
            super().__init__(s, **kwargs)
        if self.token.s not in {'p', 'r', 's'}:
            raise ValueError(f"@{self.token.s}: not a player selector token")
        

class _Relative:
    def __init__(self, val=None):
        self.val = val

    def __bool__(self):
        return False

    def __add__(self, val):
        if isinstance(val, _Relative):
            if val.val is None:
                # ~x + ~ = ~x
                # ~ + ~ = ~
                return self
            val_float = val.val
        else:
            # ~x + y = ~(x + y) to support intuitive +=
            val_float = val
            print_debug(f'interpreting {type(val)}({val}) as _Relative for _Relative.__add__')

        return _Relative((0 if self.val is None else self.val) + val_float)

    def __radd__(self, val):
        # self is not _Relative; return float
        # x + ~y = (x + y)
        return val + (0 if self.val is None else self.val)
    
    def __neg__(self):
        self.val = -self.val

    def __sub__(self, val):
        return self + -val
    
    def __round__(self, precision):
        self.val = round(self.val, precision)
    
    @staticmethod
    def join(val0, val1):
        if isinstance(val1, _Relative):
            return val0 + val1
        # ~x join y = y to support optimization of repeated teleports
        return val1
    
    def __str__(self):
        if self.val is not None:
            return '~' + str(self.val)
        return '~'

class Pos(Serializable):
    """
    Class for relative coordinates for `minecraft:vec3`.
    """
    def __init__(self, x=_Relative(), y=_Relative(), z=_Relative(), type_=None):
        """
        Defines positions, e.g. 0 128 0
        """
        self._type: Literal['^'] | None = type_
        self.vec3 = x, y, z
    
    @classmethod
    def relative(cls, x=0, y=0, z=0):
        """
        Defines relative positions, e.g. ~ ~1 ~
        """
        return cls(_Relative(x), _Relative(y), _Relative(z))

    @classmethod
    def angular(cls, left=0, up=0, forward=0):
        """
        Defines relative angular positions, e.g. ^ ^ ^5
        """
        return cls(left, up, forward, _type='^')
    
    def __add__(self, pos: Self) -> Self:
        assert self._type != '^' and pos._type != '^'
        
        return Pos(*(x0 + x1 for x0, x1 in zip(self.vec3, pos.vec3)))
    
    def join(self, pos: Self) -> Self:
        if self._type == '^' or pos._type == '^':
            raise TypeError('Invalid type for joining positions: angular')
        
        return Pos(*(_Relative.join(x0, x1) for x0, x1 in zip(self.vec3, pos.vec3)))

    def __str__(self):
        if self._type is None:
            return ' '.join(f'{round(coord, 5)}' for coord in self.vec3)
        else:
            return ' '.join(f'{self._type}{round(coord, 5) if coord else ''}' for coord in self.vec3)


class Heightmap(StrEnum):
    surface = 'world_surface'
    ocean_floor = 'ocean_floor'
    motion_blocking = 'motion_blocking'
    motion_blocking_no_leaves = 'motion_blocking_no_leaves'


class Rot(Serializable):
    """
    Class for defining `minecraft:rotation`
    """
    def __init__(self, yaw=_Relative(), pitch=_Relative(), relative=False):
        """
        Defines an absolute rotation in degrees

        yaw: 0.0 is south (+Z), 90.0 is west (-X), 180.0==-180.0 is north (-Z), -90.0 is east (+X)
        pitch: -90.0 is down (-Y), 90.0 is up (+Y)
        """
        if isinstance(yaw, _Relative):
            self.yaw = yaw
        else:
            self.yaw = (yaw + 180) % 360 - 180
        if not isinstance(pitch, _Relative):
            assert -90 <= pitch <= 90
        self.pitch = pitch
        self.relative = relative

    def __add__(self, yaw=0, pitch=0):
        return Pos(self.yaw + yaw, self.pitch + pitch)

    def __str__(self):
        if self.relative:
            return f'~{self.yaw if self.yaw else ''} ~{self.pitch if self.pitch else ''}'
        else:
            return f'{self.yaw} {self.pitch}'
        
    @classmethod
    def relative(cls, yaw=0, pitch=0):
        return cls(yaw=yaw, pitch=pitch, relative=True)

class ResourceLocation(Serializable):
    def __init__(self, namespace, path):
        self.token: ResourceLocToken = ResourceLocToken(namespace, path)

class ExternalResourceLocation(Serializable):
    def __init__(self, namespace, path):
        self.token: ResourceLocToken = ResourceLocToken(namespace, path)

class Dimension(ResourceLocation):
    def __init__(self, dimension_name: _BuiltinDimensionLiteral):
        """
        Type for a builtin minecraft dimension
        """
        super().__init__('minecraft', [dimension_name])

    @classmethod
    def external_ref(cls, namespace, dimension_path) -> Self:
        """
        Reference a dimension from any namespace
        """
        if isinstance(dimension_path, str):
            dimension_path = dimension_path.split('/')
        return ExternalResourceLocation(namespace, dimension_path)
    
class Objective(Serializable):
    def __init__(self, name: str | None = None):
        if name is None:
            name = GLOBALS.gen_name('objective')
        self.name = name

    def __str__(self):
        return self.name

class _Relation(Serializable):
    def __init__(self,
                 relation: 
                    Literal['attacker'] | 
                    Literal['controller'] |
                    Literal['leasher'] |
                    Literal['origin'] |
                    Literal['owner'] |
                    Literal['passengers'] |
                    Literal['target'] |
                    Literal['vehicle']
                 ):
        self.relation = relation

    def __str__(self):
        return self.relation

_Seconds = 20
_Days = 24000

from typing import Self, List, Dict
import json

class JSONtemplate:
    def __init__(self, type_dict: dict, cls_dict: dict):
        self.type_dict = type_dict
        self.cls_dict = cls_dict

class JSON:
    sub = int | float | str | bool | None | Self

    __slots__ = ('obj', 'template')

    def __init__(self, template=None, **obj):
        self.obj: Dict[str, 'JSON.sub' | List['JSON.sub']]
        self.template: JSONtemplate

        super().__setattr__('obj', obj)
        super().__setattr__('template', template)

    def __setattr__(self, name: str, value: 'JSON.sub' | List['JSON.sub']):
        self.obj[name] = value

    def __getattr__(self, name: str) -> 'JSON.sub' | List['JSON.sub']:
        try:
            return self.obj[name]
        except KeyError:
                raise AttributeError
        
    def __repr__(self) -> str:
        return 'JSON(' + ', '.join(f'{key}={val}' for key, val in self.obj.items()) +')'
    
    def __str__(self) -> str:
        return str(self.obj)
    
    def serialize(self, debug=False, color=False):
        if debug:
            return json.dumps(self.obj, indent=2, sort_keys=True)
        else:
            return json.dumps(self.obj)
    
    def add(self, json: Self):
        for name, val in json.obj.items():
            if name in self.obj.keys():
                match val:
                    case JSON(_):
                        self.obj[name].add(val)
                    case int(_) | float(_) | str(_) | bool(_) | None:
                        self.obj[name] = val
                    case list(_):
                        # assume no duplicates; also don't recurse into list(JSON(_))
                        # don't use set to preserve order and existing duplicates
                        self.obj[name] += [v for v in val if v not in self.obj[name]]
            else:
                self.obj[name] = val
    
    def strict_add(self, json: Self):
        self.add(json)
        return

        # TODO
        assert self.template is not None, "Improper use of strict_add without JSONtemplate"
        for name, val in json.obj.items():
            if name in self.template.keys():
                assert isinstance(val, self.template.type_dict[name])
            else:
                assert False
            match val:
                case JSON(_):
                    self.obj[name].strict_add(val)
                case int(_) | float(_) | str(_) | bool(_) | None:
                    self.obj[name] = val
                case list(_):
                    subtype = self.template[name]
                    self.obj[name] += [v for v in vals if v not in self.obj[name]]

class FunctionJSON(JSON):
    def __init__(self, functions: List[str] = []):
        super().__init__(# $optional: replace=False,
                         values=functions # list of function resource locations and function tags e.g. #namespace:path/to/tag
                         )
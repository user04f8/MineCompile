# from typing import Set, Callable, TypeVar, Generic
# from dataclasses import dataclass

# # https://minecraft.wiki/w/NBT_format

# class ParseError(Exception):
#     pass

# T = TypeVar('T')

# class Numeric(Generic[T]):
#     POSTFIX: Set[str]
#     TYPE: type = T
#     CONSTRUCTOR: Callable[[str], T]
#     MIN: T
#     MAX: T

#     def __init__(self, value: T):
#         self._value = value
    
#     @property
#     def value(self):
#         return self._value
    
#     @value.setter
#     def value(self, value):
#         if not isinstance(value, int):
#             raise TypeError("Value must be an integer")
#         if not (self.MIN <= value <= self.MAX):
#             raise ValueError("Value must be between 0 and 255")
#         self._value = value

#     @classmethod
#     def from_str(cls, s):
#         if s[-1] in cls.POSTFIX:
#             return cls(cls.CONSTRUCTOR(s)) 
#         elif '' in cls.POSTFIX:
#             return cls(cls.CONSTRUCTOR(s))
#         else:
#             raise ParseError('Invalid postfix for numeric')

# class Byte(Numeric):
#     POSTFIX = {'b', 'B'}

#     def __init__(self, value):
#         self._value = bytes([value])

# class Boolean(Byte):
#     """
#     Technically an interpretation of a byte value, but we'll keep these separate in the metalanguage
#     """
#     FALSE = Byte(0)
#     TRUE = Byte(1)

#     def from_str(self, s):
#         return {
#             'false': self.FALSE,
#             'true': self.TRUE
#         }[s]

# class Short(Numeric):
#     pass

    



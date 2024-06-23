
class Category:
    pass

class CategoryMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        return cls

class EnchantmentMeta(CategoryMeta):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        return cls

class Enchantment(Category, metaclaas=EnchantmentMeta):
    DESCRIPTION: str
    


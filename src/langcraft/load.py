from .base import Namespace, OnLoadFun, Debug

def legacy_init(namespace=None):
    if namespace:
        Namespace(namespace).__enter__()
        with OnLoadFun():
            Debug(f'langcraft datapack "{namespace}" ON', include_selector=False)
    else:
        with OnLoadFun():
            Debug(f'langcraft datapack ON', include_selector=False)



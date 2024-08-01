from langcraft import compile_all, display_all

tests = []

def test(validate=None):
    def wrapper(f):
        def inner():
            f()
            out = compile_all()
            
            if validate:
                assert validate == out, display_all(validate, out)
            else:
                display_all(out)
        tests.append(inner)
    return wrapper
    # return lambda: None



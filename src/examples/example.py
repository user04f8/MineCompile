from langcraft import *

@public
def main():
    Debug('test')
    with While('block ~ ~ ~ air'):
        Debug('test')
    
    with ScoreTree('key'):
        for i in range(0x1):
            Debug(f'key={i}')

    with Fragment() as f:
        Debug('overflow')
        Debug(f'key>{i}')

display_all()
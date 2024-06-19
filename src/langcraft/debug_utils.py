from termcolor import cprint
from traceback import print_exc

DEBUG = False

def print_fatal(msg):
    cprint(f'FATAL: {msg}', 'red')
    print_exc()

def print_err(msg):
    cprint(f'ERROR: {msg}', 'red', attrs=['reverse'])

def print_warn(msg):
    cprint(f'WARN: {msg}', 'yellow')

def print_debug(msg):
    if DEBUG:
        cprint(f'debug: {msg}', 'light_grey')

def print_debug_colorful(msg, c='green'):
    if DEBUG:
        cprint(f'debug: {msg}', c)
import ply.lex as lex
import csv

tokens = (
    'HEADER',
    'SERVER',
    'PORT',
    'CHANNEL_NAME',
    'PASSWORD',
)

t_SERVER = r'irc://[a-z0-9]+'
t_PORT = r':\d{1,5}'
t_CHANNEL_NAME = r'/[a-z0-9]+'
t_PASSWORD = r'\?[a-z0-9]+'

def t_error(t):
    t.lexer.skip(1)
    return t

lexer = lex.lex()

def Check_lex(string):

    if len(string.lower()) > 80:
        return None

    lexer.input(string)

    tok = lexer.token()
    if not tok:
        return None
    elif tok.type != 'SERVER':
            return None
    server = tok.value[6:]
    
    tok = lexer.token()
    if not tok:
        return server
    elif tok.type != 'PORT':
        return None
    elif int(tok.value[1:]) > 65535:
        return None

    tok = lexer.token()
    if not tok:
        return server
    elif tok.type != 'CHANNEL_NAME':
        return None

    tok = lexer.token()
    if not tok:
        return server
    elif tok.type != 'PASSWORD':
        return None

    tok = lexer.token()
    if not tok:
        return server
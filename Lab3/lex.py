import re
import ply.lex as lex

tokens = (
    'OPEN', 'CLOSE', 'FOPEN', 'FCLOSE', 'SOPEN', 'SCLOSE', 'COMA', 'ES',
    'AVAR', 'LVAR', 'A1ARR', 'L1ARR', 'A2ARR', 'L2ARR',
    'CAVAR', 'CLVAR',
    'LCONST', 'ACONST',
    'MOVE', 'GET', 'PUSH', 'UNDO',
    'ID',
    'EXTEND1', 'EXTEND2', 'SIZE1', 'SIZE2',
    'EQ', 'INCDEC', 'NOT', 'OR', 'GTLT',
)

ident = r'\b[A-Za-z_]\w*'

t_OPEN = r'\('
t_CLOSE = r'\)'
t_FOPEN = r'\{'
t_FCLOSE = r'\}'
t_SOPEN = r'\['
t_SCLOSE = r'\]'
t_COMA = r','
def t_ES(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_AVAR = r'UINT' + ident
t_LVAR = r'BOOLEAN' + ident
t_A1ARR = r'1DARRAYOFUINT' + ident
t_L1ARR = r'1DARRAYOFBOOL' + ident
t_A2ARR = r'2DARRAYOFUINT' + ident
t_L2ARR = r'2DARRAYOFBOOL' + ident

t_CAVAR = r'CUINT' + ident
t_CLVAR = r'CBOOLEAN' + ident

t_LCONST = r'TRUE|FALSE'
t_ACONST = r'0|[1-9][0-9]*'

t_MOVE = r'FORW|BACK|RIGHT|LEFT'
t_GET = r'GET(F|B|R|L)'
t_PUSH = r'PUSH(F|B|R|L)'
t_UNDO = r'UNDO'

t_ID = ident

t_EXTEND1 = r'EXTEND1'
t_EXTEND2 = r'EXTEND2'
t_SIZE1 = r'SIZE1'
t_SIZE2 = r'SIZE2'

t_EQ = r'='
t_INCDEC = r'INC|DEC'
t_NOT = r'NOT'
t_OR = r'OR'
t_GTLT = r'GT|LT'

t_ignore = ' \t\r\f'

def t_comment(t):
    r'\#.*\n'
    pass

def t_error(t):
    raise Exception("Lex error. Symbol: {}.".format(t.value))


lexer = lex.lex(reflags=re.UNICODE | re.VERBOSE)

text = '''
UINT a1_ = 1238888
CUINT a2 = a1
CBOOLEAN b1 = TRUE
CBOOLEAN b2 = b1


a1 = INC 23
'''

lexer.input(text)

tok = lexer.token()
while tok:
    tok = lexer.token()
    print(tok)


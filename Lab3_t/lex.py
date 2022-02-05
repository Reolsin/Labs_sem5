import re
import ply.lex as lex

tokens = (
    'OPEN', 'CLOSE', 'FOPEN', 'FCLOSE', 'SOPEN', 'SCLOSE', 'COMA', 'COMD', 'ES', 'EQ',
    'AVAR', 'LVAR', 'A1ARR', 'L1ARR', 'A2ARR', 'L2ARR',
    'CAVAR', 'CLVAR',
    'LCONST', 'ACONST',
    'MOVE', 'GET', 'PUSH', 'UNDO',
    'EXTEND1', 'EXTEND2', 'SIZE1', 'SIZE2',
    'IF', 'ELSE', 'WHILE', 'DO', 'FUNCTION',
    'INCDEC', 'NOT', 'OR', 'GTLT',
    'ID',
)


t_OPEN = r'\('
t_CLOSE = r'\)'
t_FOPEN = r'\{'
t_FCLOSE = r'\}'
t_SOPEN = r'\['
t_SCLOSE = r'\]'
t_COMA = r','
t_COMD = r';'
t_EQ = r'='
def t_ES(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

t_AVAR = r'UINT'
t_LVAR = r'BOOLEAN'
t_A1ARR = r'1DARRAYOFUINT'
t_L1ARR = r'1DARRAYOFBOOL'
t_A2ARR = r'2DARRAYOFUINT'
t_L2ARR = r'2DARRAYOFBOOL'

t_CAVAR = r'CUINT'
t_CLVAR = r'CBOOLEAN'

t_LCONST = r'TRUE|FALSE'
t_ACONST = r'0|[1-9][0-9]*'

t_MOVE = r'FORW|BACK|RIGHT|LEFT'
t_GET = r'GET(F|B|R|L)'
t_PUSH = r'PUSH(F|B|R|L)'
t_UNDO = r'UNDO'

t_EXTEND1 = r'EXTEND1'
t_EXTEND2 = r'EXTEND2'
t_SIZE1 = r'SIZE1'
t_SIZE2 = r'SIZE2'

t_IF = r'IF'
t_ELSE = r'ELSE'
t_WHILE = r'WHILE'
t_DO = r'DO'
t_FUNCTION = r'FUNCTION'

t_INCDEC = r'INC|DEC'
t_NOT = r'NOT'
t_OR = r'OR'
t_GTLT = r'GT|LT'

maxidlen = 0
def t_ID(t):
    r'\b[a-z_]\w*'
    global maxidlen
    if len(t.value) > maxidlen:
        maxidlen = len(t.value)
    return t

t_ignore = ' \t\r\f'

def t_comment(t):
    r'\#.*'
    pass

def t_error(t):
    raise Exception("Lex error. Symbol: {}.".format(t.value))


lexer = lex.lex(reflags=re.UNICODE | re.VERBOSE)

text = '''
UINT a1 = 1238888 #asdadasdasd
UINT a2
CBOOLEAN a3 = TRUE
CUINT c1 = 123
1DARRAYOFUINT arr1 = [123, a1, 42]
2DARRAYOFUINT arr2 = [123, a1, 42; 123, a1, 41;]
a4 = 0 FUNCTION test () {}
[a4 = 0, a5 = 123,] FUNCTION test (a2 = 5, a3 = 123,) {

    es = 1203
    EXTEND1 a9 5
    EXTEND2 a9 5 34

}
[a4 = 0, a5 = 123] FUNCTION test2 (a2 = 5, a3 = 123) {}

[,] = test (,)

123
TRUE

WHILE a3 DO {
    a3 = FALSE
}

IF NOT a3 {
    a3 = FALSE
}

IF a3 {
    a3 = FALSE
} ELSE { 
    a3=TRUE
}

'''

'''
(123 GT 125) OR FALSE
( NOT (123 GT 125)) OR FALSE
(123 GT 125) OR TRUE
NOT (123 GT 125) OR FALSE
'''



print(text)

# lexer.input(text)

# t = lexer.token()
# while t:
#     print(t)
#     t = lexer.token()
# print()

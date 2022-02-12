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
    'PRINT',
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

t_PRINT = r'PRINT'

t_ID = r'\b[a-z_]\w*'

t_ignore = ' \t\r\f'

def t_comment(t):
    r'\#.*'
    pass

def t_error(t):
    raise Exception("Error. Unexpected token: {}.".format(t.value))


lexer = lex.lex(reflags=re.UNICODE | re.VERBOSE)

#declarations
'''
UINT a3 = 5
PRINT a3
UINT a3
PRINT a3
CUINT a3 = 5
PRINT a3
1DARRAYOFUINT a3 = [1, 2, 3]
PRINT a3
2DARRAYOFUINT a3 = [1, 2, 3; ; 3, 2, 1]
PRINT a3
BOOLEAN a3 = FALSE
PRINT a3
BOOLEAN a3
PRINT a3
CBOOLEAN a3 = FALSE
PRINT a3
1DARRAYOFBOOL a3 = [TRUE, FALSE]
PRINT a3
2DARRAYOFBOOL a3 = [TRUE, FALSE; ; ;TRUE, FALSE]
PRINT a3'''

'''
CUINT a3 = 5
1DARRAYOFUINT a3 = [a3, a3, a3]
PRINT a3

result =  FUNCTION fib ()
'''

#factorial
'''
UINT a
res = 0 FUNCTION sum(first = 0, second = 0) {
    WHILE second GT 0 DO {
        INC first
        DEC second
        }
    res = first
}

res = 0 FUNCTION mul(f = 0, s = 0) {
    INC s
    WHILE (DEC s) GT 0 DO {
        [res] = sum(res, f)
    }
}

res = 0 FUNCTION factorial(int = 1) {
    UINT tmp = int
    IF int GT 1 {
        [tmp] = factorial(DEC tmp)
        [res] = mul(int, tmp)
    } ELSE {
        res = 1
    }
}

res = 1 FUNCTION while_factorial(int = 1) {
    UINT i = 1
    WHILE i LT int DO {
        INC i
        [res] = mul(res, i)
    }
}

[a] = sum(5, 5)
PRINT a
[a] = mul(5, 5)
PRINT a
[a] = factorial(3)
PRINT a
[a] = while_factorial(4)
PRINT a
'''

#robot prog
text = '''
WHILE LEFT DO BACK

WHILE TRUE DO {
    IF RIGHT {
        WHILE LEFT DO {}
    }
}
'''

#fibonachi
'''
res = 0 FUNCTION sum(first = 0, second = 0) {
    WHILE second GT 0 DO {
        INC first
        DEC second}
    res = first
}
res = 0 FUNCTION fib(int = 1) {
    UINT b = 1
    UINT t
    WHILE b LT int DO {
        PRINT b
        t = b
        [b] = sum(res,b)
        res = t
        }
    }

UINT a
[a] = fib(9)

'''


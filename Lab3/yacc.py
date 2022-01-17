from lex import tokens
import ply.yacc as yacc

def p_prog(p):
    '''prog : 
            | prog decl ES
            | prog cdecl ES
            | prog expr ES
            | prog expr ES'''




def p_decl(p):
    '''decl : AVAR
            | AVAR EQ ACONST
            | AVAR EQ expr'''

def p_cdecl(p):
    '''decl : CAVAR EQ ACONST
            | CLVAR EQ LCONST'''

def p_expr(p):
    '''expr : INCDEC expr
            | INCDEC ACONST
            | INCDEC ID'''
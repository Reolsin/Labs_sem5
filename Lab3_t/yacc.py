from msilib.schema import Error
from lex import tokens, text, maxidlen
import ply.yacc as yacc

class Var:

    def __init__(self, id, type, data) -> None:
        self.id = id
        self.type = type
        self.data = data

    def __repr__(self) -> str:
        return 'Var      | ID: {} | Type: {} | Data: {}\t'.format(self.id + ''.join([' ' for i in range(maxidlen-len(self.id))]), self.type + ''.join([' ' for i in range(13-len(self.type))]), self.data)

class Function:
    
    def __init__(self, id, pars, group, vars) -> None:
        self.id = id
        self.id_pars = pars
        self.id_vars = vars
        self.group = group

    def __repr__(self) -> str:
        out = 'Function | ID: '
        out += self.id + ''.join([' ' for i in range(maxidlen-len(self.id))])
        out += ' | Parameters: '
        if self.id_pars:
            out += str(self.id_pars)
        else:
            out += 'None'
        out += ' | Return vars: '
        if self.id_vars:
            out += str(self.id_vars)
        else:
            out += 'None'
        out += '\n{\n\t'
        if self.group:
            out += self.group.parts_str().replace('\n', '\n\t')
        out += '\n}'
        return out

class Expression:

    def __init__(self, type, left, right):
        self.type = type
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return str(self.left)

class GT(Expression):

    def __init__(self, first: Expression, second: Expression):
        if first.type == 'A' and second.type == 'A':
            if int(first.left) > int(second.left):
                super().__init__('L', 'TRUE', None)
            else:
                super().__init__('L', 'FALSE', None)
        elif first.type == 'L' or second.type == 'L':
            raise Exception('Incorrect types.')
        else:
            super().__init__('I', first, second)

    def __repr__(self) -> str:
        if self.right:
            return '( {} GT {} )'.format(self.left, self.right)
        else:
            return str(self.left)

    def Solve(self):
        pass

class LT(Expression):

    def __init__(self, first: Expression, second: Expression):
        if first.type == 'A' and second.type == 'A':
            if int(first.left) < int(second.left):
                super().__init__('L', 'TRUE', None)
            else:
                super().__init__('L', 'FALSE', None)
        elif first.type == 'L' or second.type == 'L':
            raise Exception('Incorrect types.')
        else:
            super().__init__('I', first, second)

    def __repr__(self) -> str:
        if self.right:
            return '( {} LT {} )'.format(self.left, self.right)
        else:
            return str(self.left)
    
    def Solve(self):
        pass

class OR(Expression):

    def __init__(self, first: Expression, second: Expression):
        if first.type == 'L' and second.type == 'L':
            if first.left == 'TRUE' or second.left == 'TRUE':
                super().__init__('L', 'TRUE', None)
            else:
                super().__init__('L', 'FALSE', None)
        elif first.type == 'A' or second.type == 'A':
            raise Exception('Incorrect types.')
        else:
            super().__init__('I', first, second)

    def __repr__(self) -> str:
        if self.right:
            return '( {} OR {} )'.format(self.left, self.right)
        else:
            return str(self.left)

    def Solve(self):
        pass

class NOT(Expression):

    def __init__(self, first: Expression):
        if first.type == 'L':
            if first.left == 'TRUE':
                super().__init__('L', 'FALSE', None)
            else:
                super().__init__('L', 'TRUE', None)
        elif first.type == 'A':
            raise Exception('Incorrect types.')
        else:
            super().__init__('I', first, None)

    def __repr__(self) -> str:
        if self.type == 'I':
            return '( NOT {} )'.format(self.left)
        else:
            return str(self.left)

    def Solve(self):
        pass

class INC(Expression):

    def __init__(self, first: Expression):
        if first.type == 'I':
            super().__init__('I', first, None)
        else:
            raise Exception('Incorrect types.')

    def __repr__(self) -> str:
        if self.type == 'I':
            return '( NOT {} )'.format(self.left)
        else:
            return str(self.left)

    def Solve(self):
        pass

class DEC(Expression):

    def __init__(self, first: Expression):
        if first.type == 'I':
            super().__init__('I', first, None)
        else:
            raise Exception('Incorrect types.')

    def __repr__(self) -> str:
        if self.type == 'I':
            return '( NOT {} )'.format(self.left)
        else:
            return str(self.left)

    def Solve(self):
        pass


class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace('\n', '\n\t')

    def add_parts(self, parts):
        self.parts += parts
        return self

    def add_part(self, part):
        self.parts.append(part)
        return self

    def __init__(self, type, parts: list):
        self.type = type
        self.parts = parts

#-GRAMMAR------------------------------------------------------------

def p_prog(p):
    '''prog : prog line es
            | prog fdecl es'''
    if p[1]:
        if p[2]: p[0] = p[1].add_part(p[2])
        else: p[0] = p[1]
    else:
        if p[2]: p[0] = Node('prog', [p[2]])
        else: p[0] = None

def p_prog_empty(p):
    '''prog : '''
    p[0] = None

def p_es(p):
    '''es : es es
          | ES'''

def p_line(p):
    '''line : sent
            | logic
            | fcall
            | group
            | decl
            | cdecl'''
    p[0] = p[1]

def p_line_empty(p):
    '''line : '''
    p[0] = None

def p_sent_eq(p):
    '''sent : ID EQ expr'''
    p[0] = Node(p[2], [p[1], p[3]])

def p_sent_extend(p):
    '''sent : EXTEND1 ID expr
            | EXTEND2 ID expr expr'''
    p[0] = Node(p[1], p[2:])

def p_sent_exun(p):
    '''sent : expr
            | UNDO'''
    p[0] = p[1]

def p_group(p):
    '''group : FOPEN lines line FCLOSE
             | FOPEN lines FCLOSE'''
    if len(p) == 5:
        if p[2]:
            p[0] = Node('group', p[2] + [p[3]])
        else:
            p[0] = Node('group', [p[3]])
    else:
        if p[2]:
            p[0] = Node('group', p[2])
        else:
            p[0] = Node('group', [p[2]])

def p_lines(p):
    '''lines : lines line es'''
    if p[1]:
        if p[2]:
            p[0] = p[1].append(p[2])
        p[0] = p[1]
    elif p[2]:
        p[0] = [p[2]]
    else: 
        p[0] = None

def p_lines_empty(p):
    '''lines : '''
    p[0] = None

#-DECLARATIONS------------------------------------------------------------

def p_decl(p):
    '''decl : 2ldecl
            | 2adecl
            | 1ldecl
            | 1adecl
            | lvdecl
            | avdecl'''
    p[0] = p[1]

def p_cdecl(p):
    '''cdecl : cldecl
             | cadecl'''
    p[0] = p[1]

#-CONST-DECL------------------------------------------------------------

def p_cldecl(p):
    '''cldecl : CLVAR ID EQ expr'''
    p[0] = Var(p[2], p[1], p[4])

def p_cadecl(p):
    '''cadecl : CAVAR ID EQ expr'''
    p[0] = Var(p[2], p[1], p[4])

#-VAR-DECL------------------------------------------------------------

def p_lvdecl(p):
    '''lvdecl : LVAR ID
              | LVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], p[1], p[4])
    else:
        p[0] = Var(p[2], p[1], None)

def p_avdecl(p):
    '''avdecl : AVAR ID
              | AVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], p[1], p[4])
    else:
        p[0] = Var(p[2], p[1], None)

#-ARR-DECL------------------------------------------------------------

def p_1ldecl(p):
    '''1ldecl : L1ARR ID
              | L1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], p[1], None)
    else:
        p[0] = Var(p[2], p[1], p[5])

def p_1adecl(p):
    '''1adecl : A1ARR ID
              | A1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], p[1], None)
    else:
        p[0] = Var(p[2], p[1], p[5])

def p_2ldecl(p):
    '''2ldecl : L2ARR ID
              | L2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], p[1], None)
    else:
        p[0] = Var(p[2], p[1], p[5])

def p_2adecl(p):
    '''2adecl : A2ARR ID
              | A2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], p[1], None)
    else:
        p[0] = Var(p[2], p[1], p[5])

def p_vals(p):
    '''vals : expr COMA vals
            | expr'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_arrs(p):
    '''arrs : vals COMD arrs
            | COMD arrs
            | vals'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[2] + [None]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]

def p_arrs_empty(p):
    '''arrs : '''
    p[0] = [None]

#-FUNC-DECL------------------------------------------------------------

def p_fdecl(p):
    '''fdecl : fovars FUNCTION ID fivars group'''
    p[0] = Function(p[3], p[4], p[5], p[1])
    # p[0] = Node(p[2], [p[3], p[4], p[1], p[5]])

def p_fovars(p):
    '''fovars : ID EQ expr'''
    # p[0] = Node(p[1], [p[3]])
    p[0] = [[p[1], p[3]]]

def p_fovars_br(p):
    '''fovars : SOPEN fvars SCLOSE'''
    # if p[2]:
    #     p[2].type = 'fovars'
    p[0] = p[2]

def p_fivars(p):
    '''fivars : OPEN fvars CLOSE'''
    # if p[2]:
    #     p[2].type = 'fivars'
    p[0] = p[2]

def p_fvars(p):
    '''fvars : ID EQ expr
             | ID EQ expr COMA fvars'''
    # if len(p) == 6 and p[5]:
    #     p[0] = p[5].add_part(Node(p[1], [p[3]]))
    # else:
    #     p[0] = Node('fvars', [Node(p[1], [p[3]])])
    if len(p) == 6 and p[5]:
        p[0] = [[p[1], p[3]]] + p[5]
    else:
        p[0] = [[p[1], p[3]]]

def p_fvars_empty(p):
    '''fvars : '''
    p[0] = None

#-EXPRESSIONS------------------------------------------------------------

def p_expr(p):
    '''expr : oper
            | ACONST
            | LCONST
            | ID
            | INCDEC ID
            | NOT expr
            | expr GTLT expr
            | expr OR expr
            | OPEN expr CLOSE'''
    if len(p) == 2:
        if p[1].isdigit():
            p[0] = Expression('A', p[1], None)
        elif p[1] == 'TRUE' or p[1] == 'FALSE':
            p[0] = Expression('L', p[1], None)
        else:
            p[0] = Expression('I', p[1], None)
    elif len(p) == 3:
        if p[1] == 'INC':
            p[0] = INC(p[2])
        elif p[1] == 'DEC':
            p[0] = DEC(p[2])
        else:
            p[0] = NOT(p[2])
    else:
        if p[2] == 'GT':
            p[0] = GT(p[1], p[3])
        elif p[2] == 'LT':
            p[0] = LT(p[1], p[3])
        elif p[2] == 'OR':
            p[0] = OR(p[1], p[3])
        else:
            p[0] = p[2]

def p_oper(p):
    '''oper : MOVE
            | GET
            | PUSH
            | SIZE1 ID
            | SIZE2 ID expr
            | ID OPEN expr COMA expr CLOSE
            | ID OPEN expr CLOSE'''
    p[0] = 'oper'

#-LOGIC------------------------------------------------------------

def p_logic(p):
    '''logic : cond
             | loop'''
    p[0] = p[1]

def p_cond(p):
    '''cond : IF expr sent else
            | IF expr group else'''
    if p[4]:
        p[0] = Node(p[1], [p[2], p[3], p[4]])
    else:
        p[0] = Node(p[1], [p[2], p[3]])

def p_else(p):
    '''else : ELSE sent
            | ELSE group'''
    p[0] = p[2]
    
def p_else_empty(p):
    '''else : '''
    p[0] = None

def p_loop(p):
    '''loop : WHILE expr DO sent
            | WHILE expr DO group'''
    p[0] = Node(p[1], [p[2], p[4]])

#-CALLS------------------------------------------------------------

def p_fcall(p):
    '''fcall : SOPEN vars SCLOSE EQ ID OPEN pars CLOSE'''
    p[0] = Node('fcall', [p[5], p[7], p[2]])

def p_vars(p):
    '''vars : ID COMA vars
            | COMA vars
            | ID'''
    if len(p) == 4:
        p[0] = p[3].add_part(p[1])
    elif len(p) == 3:
        p[0] = p[2].add_part(None)
    else:
        p[0] = Node('vars', [p[1]])

def p_vars_empty(p):
    '''vars : '''
    p[0] = Node('vars', [None])

def p_pars(p):
    '''pars : expr COMA pars
            | COMA pars
            | expr'''
    if len(p) == 4:
        p[0] = p[3].add_part(p[1])
    elif len(p) == 3:
        p[0] = p[2].add_part(None)
    else:
        p[0] = Node('pars', [p[1]])

def p_pars_empty(p):
    '''pars : '''
    p[0] = Node('pars', [None])

#-PARSER------------------------------------------------------------

parser = yacc.yacc()

def build_tree(code):
    return parser.parse(code)

prog = build_tree(text+'\n')

print(prog)


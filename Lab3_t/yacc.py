from lex import tokens, text
import ply.yacc as yacc

vars = dict()
functions = dict()

class Var:

    def __init__(self, id, type, data) -> None:
        self.id = id
        self.type = type
        self.data = data

    def _type(self):
        if self.type == '1DARRAYOFUINT' or self.type == '2DARRAYOFUINT' or self.type == 'UINT' or self.type == 'CUINT':
            return 'UINT'
        else:
            return 'BOOL'

    def const(self):
        return self.type == 'CBOOLEAN' or self.type == 'CUINT'

    def array(self):
        return self.type[1] == 'D'

    def dimension(self):
        return self.type[0].isdigit()

    def __repr__(self) -> str:
        return 'Var      | ID: {} | Type: {} | Data: {}\t'.format(self.id + ' '*(10-len(self.id)), self.type + ' '*(13-len(self.type)), self.data)

class Function:
    
    def __init__(self, id, pars, group, vars) -> None:
        self.id = id
        self.vars = set()
        self.id_pars = pars
        self.id_vars = vars
        self.group = group

    def __repr__(self) -> str:
        out = 'Function | ID: '
        out += self.id + ' '*(10-len(self.id))
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
            out += '\n'.join([str(i) for i in self.group]).replace('\n', '\n\t')
        out += '\n}'
        return out

class Expression:

    def __init__(self):
        pass

class CONST(Expression):

    def __init__(self, type, val):
        self.type = type
        self.val = val

    def __repr__(self) -> str:
        return str(self.val)

class GT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} GT {} )'.format(self.left, self.right)

    def Solve(self):
        pass

class LT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} LT {} )'.format(self.left, self.right)
    
    def Solve(self):
        pass

class OR(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} OR {} )'.format(self.left, self.right)

    def Solve(self):
        pass

class NOT(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self):
        pass

class INC(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self):
        pass

class DEC(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self):
        pass

class Oper(Expression):

    def __init__(self, operator, first, second, third):
        self.type = operator
        self.first = first
        self.second = second
        self.third = third

    def __repr__(self):
        return '[{} , {} , {} , {}]'.format(self.type, self.first, self.second, self.third)

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

def _OR(first, second):
    if type(first) == CONST and type(second) == CONST:
        if first.type == 'L' and second.type == 'L':
            if first.val == 'TRUE' or second.val == 'TRUE':
                return CONST('L', 'TRUE')
            else:
                return CONST('L', 'FALSE')
        elif first.type == 'A' or second.type == 'A':
            raise Exception('Incorrect types.')
        else:
            return OR(first, second)
    else:
        return OR(first, second)

def _GT(first, second):
    if type(first) == CONST and type(second) == CONST:
        if first.type == 'A' and second.type == 'A':
            if int(first.val) > int(first.val):
                return CONST('L', 'TRUE')
            else:
                return CONST('L', 'FALSE')
        elif first.type == 'L' or second.type == 'L':
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _LT(first, second):
    if type(first) == CONST and type(second) == CONST:
        if first.type == 'A' and second.type == 'A':
            if int(first.val) < int(first.val):
                return CONST('L', 'TRUE')
            else:
                return CONST('L', 'FALSE')
        elif first.type == 'L' or second.type == 'L':
            raise Exception('Incorrect types.')
        else:
            return LT(first, second)
    else:
        return LT(first, second)

def _NOT(first):
    if type(first) == CONST:
        if first.type == 'L':
            if first.val == 'FALSE':
                return CONST('L', 'TRUE')
            else:
                return CONST('L', 'FALSE')
        elif first.type == 'A':
            raise Exception('Incorrect types.')
        else:
            return NOT(first)
    else:
        return NOT(first)

def _INC(first):
    if type(first) == CONST and first.type == 'I':
        return INC(first)
    else:
        raise Exception('Incorrect types.')

def _DEC(first):
    if type(first) == CONST and first.type == 'I':
        return INC(first)
    else:
        raise Exception('Incorrect types.')

#-GRAMMAR------------------------------------------------------------

def p_prog(p):
    '''prog : prog line es
            | prog fdecl es'''
    if p[1]:
        if p[2]: 
            if type(p[2]) == list:
                p[0] = p[1].add_parts(p[2])
            else:
                p[0] = p[1].add_part(p[2])
        else: p[0] = p[1]
    else:
        if p[2]:
            if type(p[2]) == list:
                p[0] = Node('prog', p[2])
            else:
                p[0] = Node('prog', [p[2]])
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
    '''sent : ID EQ expr
            | access EQ expr'''
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
            if type(p[3]) == list:
                p[0] = p[2] + p[3]
            else:
                p[0] = p[2] + [p[3]]
        else:
            if type(p[3]) == list:
                p[0] = p[3]
            else:
                p[0] = [p[3]]
        p[0] = p[2]
    else:
        if p[2]:
            p[0] = p[2]
        else:
            p[0] = [p[2]]

def p_lines(p):
    '''lines : lines line es'''
    if p[1]:
        if p[2]:
            if type(p[2]) == list:
                p[1].extend(p[2])
            else:
                p[1].append(p[2])
        p[0] = p[1]
    elif p[2]:
        if type(p[2]) == list:
            p[0] = p[2]
        else:
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

def p_fovars(p):
    '''fovars : ID EQ expr'''
    p[0] = [[p[1], p[3]]]

def p_fovars_br(p):
    '''fovars : SOPEN fvars SCLOSE'''
    p[0] = p[2]

def p_fivars(p):
    '''fivars : OPEN fvars CLOSE'''
    p[0] = p[2]

def p_fvars(p):
    '''fvars : ID EQ expr
             | ID EQ expr COMA fvars'''
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
            | NOT expr
            | INCDEC ID
            | expr GTLT expr
            | expr OR expr
            | OPEN expr CLOSE'''
    if len(p) == 2:
        if p[1].isdigit():
            p[0] = CONST('A', p[1])
        elif p[1] == 'TRUE' or p[1] == 'FALSE':
            p[0] = CONST('L', p[1])
        elif type(p[1]) == Oper:
            p[0] = p[1]
        else:
            p[0] = CONST('I', p[1])
    elif len(p) == 3:
        if p[1] == 'INC':
            p[0] = _INC(p[2])
        elif p[1] == 'DEC':
            p[0] = _DEC(p[2])
        else:
            p[0] = _NOT(p[2])
    else:
        if p[2] == 'GT':
            p[0] = _GT(p[1], p[3])
        elif p[2] == 'LT':
            p[0] = _LT(p[1], p[3])
        elif p[2] == 'OR':
            p[0] = _OR(p[1], p[3])
        else:
            p[0] = p[2]

def p_oper(p):
    '''oper : MOVE
            | GET
            | PUSH
            | SIZE1 ID
            | SIZE2 ID expr
            | access'''
    if len(p) == 2:
        if p[1][0:4] == 'PUSH':
            p[0] = Oper('PUSH', p[1][4], None, None)
        elif p[1][0:3] == 'GET':
            p[0] = Oper('GET', p[1][3], None, None)
        elif p[1] == 'FORW' or p[1] == 'BACK' or p[1] == 'RIGHT' or p[1] == 'LEFT':
            p[0] = Oper('MOVE', p[1][0], None, None)
        else:
            p[0] = p[1]
    elif p[1] == 'SIZE1':
        p[0] = Oper('SIZE1', p[2], None, None)
    elif p[1] == 'SIZE2':
        p[0] = Oper('SIZE2', p[2], p[3], None)


def p_access(p):
    '''access : ID OPEN expr COMA expr CLOSE
              | ID OPEN expr CLOSE'''
    if len(p) == 5:
        p[0] = Oper('()', p[1], p[3], None)
    else:
        p[0] = Oper('()', p[1], p[3], p[5])


#-LOGIC------------------------------------------------------------

def p_logic(p):
    '''logic : cond
             | loop'''
    p[0] = p[1]

def p_cond(p):
    '''cond : IF expr sent else
            | IF expr group else'''
    if p[4]:
        p[0] = Node(p[1], [p[2], Node('then',p[3]), p[4]])
    else:
        p[0] = Node(p[1], [p[2], Node('then',p[3])])

def p_else(p):
    '''else : ELSE sent
            | ELSE group'''
    p[0] = Node('else', p[2])
    
def p_else_empty(p):
    '''else : '''
    p[0] = None

def p_loop(p):
    '''loop : WHILE expr DO sent
            | WHILE expr DO group'''
    p[0] = Node(p[1], [p[2], Node('do', p[4])])

#-CALLS------------------------------------------------------------

def p_fcall(p):
    '''fcall : SOPEN vars SCLOSE EQ ID OPEN pars CLOSE
             | ID EQ ID OPEN pars CLOSE'''
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

#-MAP------------------------------------------------------------

input_file = open('map.txt')
Map = [[j for j in i if j != '\n'] for i in input_file]

#-------------------------------------------------------------



for line in prog.parts:
    if type(line) == Node:
        if line.type == 'fcall':
            if functions.get(line.parts[0]):
                func = functions[line.parts[0]]
                if len(func.pars) == len(line.parts[1]):
                    if len(func.vars) == len(line.parts[2]):
                        res = func.run(line.parts[1])
                        for i in len(line.parts[2]):
                            ident = line.parts[2][i]
                            if vars.get(ident):
                                if not vars[ident].const and vars[ident].type == res[i].type:
                                    vars[ident].data = res[i]
                                else:
                                    raise Exception('Non integer index.')
                            else:
                                raise Exception('Variable not declarated.')
                    else:
                        raise Exception('Incorrect function call, function return {} args, but {} stated.'.format(len(func.vars), len(line.parts[2])))
                else:
                    raise Exception('Incorrect function call, got {} args, but {} expected.'.format(len(line.parts[1]), len(func.pars)))
            else:
                raise Exception('Function not declarated.')
        elif line.type == '=':
            if type(line.parts[0]) == Oper:
                var = line.parts[1].first
                if vars.get(var):
                    tmp1 = line.parts[1].second.Solve()
                    if tmp1.type != 'UINT':
                        raise Exception('Non integer index.')
                    if line.parts[1].third:
                        if vars[var].type[0] == '2':
                            tmp2 = line.parts[1].Solve()
                            if tmp2.type != 'UINT':
                                raise Exception('Non integer index.')
                            tmp = line.parts[2].Solve()
                            if vars[var]._type() == tmp.type:
                                if tmp1.data < len(vars[var].data) and tmp2.data < len(vars[var].data[tmp1.data]):
                                    vars[var].data[tmp1.data][tmp2.data] = tmp.data
                                else:
                                    raise Exception('Index out of range.')
                            else:
                                raise Exception('Incorrect type.')
                        else:
                            raise Exception('Incorrect type. Array got 1 args, 2 expected.')
                    else:
                        if vars[var].type[0] == '1':
                            tmp = line.parts[2].Solve()
                            if vars[var]._type() == tmp.type:
                                if tmp1.data < len(vars[var].data):
                                    vars[var].data[tmp1.data] = tmp.data
                                else:
                                    raise Exception('Index out of range.')
                            else:
                                raise Exception('Incorrect type.')
                        else:
                            raise Exception('Incorrect type. Array got 2 args, 1 expected.')
                else:
                    raise Exception('Variable not declarated.')
            else:
                var = line.parts[0]
                if vars.get(var):
                    if not vars[var].const:
                        tmp = line.parts[1].Solve()
                        if tmp.type == vars[var].type:
                            vars[var].data = tmp.data
                        else:
                            raise Exception('Incorrect type.')
                    else:
                        raise Exception('Cant change const variable.')
                else:
                    raise Exception('Variable not declarated.')
        elif line.type == 'EXTEND1':
            var = line.parts[0]
            if vars.get(var):
                tmp = line.parts[1].Solve()
                if tmp.type != 'UINT' or not vars[var].array():
                    raise Exception('Incorrect type.')
                if tmp.data >= len(vars[var].data):
                    vars[var].data.extend([None for i in range(tmp.data - len(vars[var].data))])
                else:
                    raise Exception('Runtime error.')
            else:
                raise Exception('Variable not declarated.')
        elif line.type == 'EXTEND2':
            var = line.parts[0]
            if vars.get(var):
                tmp1 = line.parts[1].Solve()
                tmp2 = line.parts[2].Solve()
                if tmp1.type != 'UINT' or not vars[var].array() or tmp2.type != 'UINT':
                    raise Exception('Incorrect type.')
                if tmp1.data < len(vars[var].data):
                    if tmp2.data >= len(vars[var].data[tmp1.data]):
                        vars[var].data[tmp1.data].extend([None for i in range(tmp2.data - len(vars[var].data[tmp1.data]))])
                    else:
                        raise Exception('Runtime error.')
                else:
                    raise Exception('Index out of range.')
            else:
                raise Exception('Variable not declarated.')
        elif line.type == 'IF':
            pass
        elif line.type == 'WHILE':
            pass
        else:
            raise Exception('Wtf.')
    elif type(line) == Function:
        if not functions.get(line.id):
            functions[line.id] = line
        else:
            raise Exception('This function already declarated.')
    elif type(line) == Var:
        if line.data:
            line.data = line.data.Solve().data
        vars[line.id] = line
    elif type(line) == Expression:
        line.Solve()
    elif line == 'UNDO':
        pass

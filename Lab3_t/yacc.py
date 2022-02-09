from re import L
from lex import tokens, text
import ply.yacc as yacc

class Var:

    def __init__(self, id, type, data) -> None:
        self.id = id
        self.type = type
        self.data = data

    def check_dimensions(self, n):
        if self.type[0] == str(n):
            return True
        else:
            raise Exception('Expected {} index, but {} were given.'.format(self.type[0], n))

    def check_const(self):
        if self.type[0] == 'C': raise Exception('Const value cant be changed.')
        else: return False

    def check_type(self, type):
        if self.type[-4:] == 'UINT':
            if type == int: return True
            else: raise Exception('Incorrect type.')
        else:
            if type == bool: return True
            else: raise Exception('Incorrect type.')

    def init(self, program, function):
        if self.type[0] == '1':
            data = []
            for expr in self.data:
                tmp = expr.Solve()
                self.check_type(tmp.type)
                self.data = tmp.data
        elif self.type[0] == '2':
            data = []
            for array in self.data:
                arrtmp = []
                for expr in array:
                    tmp = expr.Solve()
                    self.check_type(tmp.type)
                    self.data = tmp.data
                data.append(arrtmp)
        else:
            tmp = self.data.Solve(program, function)
            self.check_type(tmp.type)
            self.data = tmp.data

    def __repr__(self) -> str:
        return 'Var      | ID: {} | Type: {} | Data: {}\t'.format(self.id + ' '*(10-len(self.id)), self.type + ' '*(13-len(self.type)), self.data)

def get_var(ident, program, function) -> Var:
    if function:
        var = function.vars.get(ident)
        if not var:
            var = program.check_var_decl(ident)
    else:
        var = program.check_var_decl(ident)
    return var

def get_aexpr(expr, program, function) -> Var:
    tmp = expr.Solve(program, function)
    tmp.check_type(int)
    return tmp

def get_lexpr(expr, program, function) -> Var:
    tmp = expr.Solve(program, function)
    tmp.check_type(bool)
    return tmp

class Function:
    
    def __init__(self, id, pars, group, vars) -> None:
        self.id = id
        self.vars = dict()
        self.id_pars = pars
        self.id_vars = vars
        self.group = group

    def check_input_count(self, n):
        if n == len(self.id_pars):
            return True
        else:
            raise Exception('Incorrect function call, got {} args, but {} expected.'.format(n, len(self.id_pars)))

    def check_out_count(self, n):
        if n == len(self.id_vars):
            return True
        else:
            raise Exception('Incorrect function call, function return {} args, but {} stated.'.format(len(self.id_vars), n))

    def init(self, program):
        for par in self.id_pars:
            tmp = par[1].Solve(program, None)
            tmp.id = par[0]
            self.vars[par[0]] = tmp
        self.id_pars = [i[0] for i in self.id_pars]
        for var in self.id_vars:
            tmp = var[1].Solve()
            tmp.id = par[0]
            self.vars[par[0]] = tmp
        self.id_vars = [i[0] for i in self.id_vars]

    def run(self, program, pars):
        pass

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
    pass

class CONST(Expression):

    def __init__(self, type, val):
        self.type = type
        self.val = val

    def __repr__(self) -> str:
        return str(self.val)

    def Solve(self, program, function) -> Var:
        if self.type == Var:
            return get_var(self.val, program, function)
        else:
            return Var(None, self.type, self.val)

class GT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} > {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Var:
        left = get_aexpr(self.left, program, function)
        right = get_aexpr(self.right, program, function)
        return Var(None, bool, left.data > right.data)

class LT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} < {} )'.format(self.left, self.right)
    
    def Solve(self, program, function) -> Var:
        left = get_aexpr(self.left, program, function)
        right = get_aexpr(self.right, program, function)
        return Var(None, bool, left.data < right.data)

class OR(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} OR {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Var:
        left = get_lexpr(self.left, program, function)
        right = get_lexpr(self.right, program, function)
        return Var(None, bool, left.data or right.data)

class NOT(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self, program, function) -> Var:
        var = get_lexpr(self.val, program, function)
        return Var(None, bool, not var.data)

class INC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '++{}'.format(self.val)

    def Solve(self, program, function) -> Var:
        var = get_aexpr(self.expr, program, function)
        var.data += 1
        var.check_const()
        return Var(None, int, var.data)

class DEC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '--{}'.format(self.val)

    def Solve(self, program, function) -> Var:
        var = get_aexpr(self.expr, program, function)
        var.data -= 1
        var.check_const()
        return Var(None, int, var.data)

class Oper(Expression):

    def __init__(self, operator, first, second):
        self.operator = operator
        self.first = first
        self.second = second

    def __repr__(self):
        return '[ {} : {} , {} ]'.format(self.operator, self.first, self.second)

    def Solve(self, program, function) -> Var:
        if self.operator == 'PUSH':
            return Var(None, bool, program.move(self.first))
        elif self.operator == 'GET':
            return Var(None, int, program.move(self.first))
        elif self.operator == 'MOVE':
            return Var(None, bool, program.move(self.first))
        elif self.operator[:-1] == 'SIZE':
            var = get_var(self.first, program, function)
            if self.second:
                tmp = get_aexpr(self.second, program, function).data
                return Var(None, int, len(var.data[tmp]))
            else:
                return Var(None, int, len(var.data))
        else:
            raise Exception('')

class Assign:

    def __init__(self, a, b: Expression):
        self.target = a
        self.expr = b

    def __repr__(self) -> str:
        return '{} := {}'.format(self.target, self.expr)

    def execute(self, program, function: Function):
        tmp = self.expr.Solve(program, function)
        if type(self.target) == Brackets:
            var = self.target.Solve(program, function)
        else:
            var = get_var(self.target, program, function)
        if var.check_type(tmp.type) and not var.check_const():
            var.data = tmp.data

class EXTEND:
    
    def __init__(self, ident, expr1, expr2):
        self.ident = ident
        self.expr1 = expr1
        self.expr2 = expr2

    def __repr__(self):
        out = self.ident + '.extend(' + str(self.expr1)
        if self.expr2:
            out += ', ' + str(self.expr2)
        out += ')'
        return out

    def execute(self, program, function: Function):
        var = get_var(self.ident, program, function)
        tmp1 = get_aexpr(self.expr1, program, function).data
        if self.expr2:
            var.check_dimensions(2)
            tmp2 = get_aexpr(self.expr2, program, function).data
            if tmp1 < len(var.data):
                if tmp2 >= len(var.data[tmp1]):
                    var.data[tmp1].extend([None for i in range(tmp2 - len(var.data[tmp1]))])
                else: raise Exception('Runtime error.')
            else: raise Exception('Index out of range.')
        else:
            var.check_dimensions(1)
            if tmp1 >= len(var.data):
                var.data[tmp1].extend([None for i in range(tmp1 - len(var.data))])
            else: raise Exception('Runtime error.')

class Brackets(Expression):

    def __init__(self, ident, i, j):
        self.ident = ident
        self.expr1 = i
        self.expr2 = j

    def __repr__(self):
        out = '{}[{}]'.format(self.ident, self.expr1)
        if self.expr2:
            out += '[{}]'.format(self.expr2)
        return out

    def Solve(self, program, function) -> Var:
        var = get_var(self.ident, program, function)
        tmp1 = get_aexpr(self.expr1, program, function).data
        if self.expr2 and var.check_dimensions(2):
            tmp2 = get_aexpr(self.expr2, program, function).data
            return var[tmp1][tmp2]
        else:
            var.check_dimensions(1)
            return var[tmp1]

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

class Condition:
    
    def __init__(self, expr, then, _else) -> None:
        self.expr = expr
        self.then = then
        self._else = _else

    def __repr__(self):
        out = 'if ' + str(self.expr) + ' then: {\n\t'
        out += '\n'.join([str(i) for i in self.then]).replace('\n', '\n\t') + '\n}'
        if self._else:
            out += ' else: {\n\t'
            out += '\n'.join([str(i) for i in self._else]).replace('\n', '\n\t') + '\n}'
        return out

    def run(self, program, function):
        if get_lexpr(self.expr, program, function).data:
            exe_gr = self.then
        else:
            exe_gr = self._else
        if exe_gr:
            for line in exe_gr:
                pass

class While:
    
    def __init__(self, expr, do) -> None:
        self.expr = expr
        self.do = do

    def __repr__(self):
        out = 'while ' + str(self.expr) + ': {\n\t'
        out += '\n'.join([str(i) for i in self.do]).replace('\n', '\n\t') + '\n}'
        return out

    def run(self, program, function):
        while get_lexpr(self.expr, program, function).data:
            for line in self.do:
                pass


class Prog:

    def __init__(self, lines):
        self.vars = dict()
        self.functions = dict()
        self.script = lines
        self.robot_map = None

    def execute(self, Map):
        if not Map:
            raise Exception('Error in loading map.')
        self.robot_map = Map
        for line in self.script:
            if type(line) == Var:
                line.init(self, None)
                self.vars[line.id] = line
            elif type(line) == Function:
                if self.functions.get(line.id):
                    raise Exception('Funtion already declarated.')
                else:
                    line.init()
                    self.functions[line.id] = line
            elif type(line) == Assign:
                line.execute(self, None)
            elif type(line) == Expression:
                line.Solve(self, None)
            elif type(line) == Condition:
                line.run(self, None)
            elif type(line) == While:
                line.run(self, None)
            elif type(line) == EXTEND:
                line.execute(self, None)
            elif type(line) == Node:
                if line.type == 'fcall':
                        func = self.check_func_decl(line.parts[0])
                        if func.check_input_count(len(line.parts[1])) and func.check_out_count(len(line.parts[2])):
                            res = func.run(self, line.parts[1])
                            for i in len(res):
                                if line.parts[2][i]:
                                    var = self.check_var_decl(line.parts[2][i])
                                    if not var.check_const() and var.check_type(res[i].type):
                                        var.data = res[i]
                else: raise Exception('')
            elif line == 'UNDO':
                pass

    def check_var_decl(self, ident) -> Var:
        if self.vars.get(ident):
            return self.vars[ident]
        else:
            raise Exception('Variable not declarated.')

    def check_func_decl(self, ident) -> Function:
        if self.functions.get(ident):
            return self.functions[ident]
        else:
            raise Exception('Function not declarated.')

    def __str__(self):
        return 'Program tree:\n\t' + '\n'.join([str(i) for i in self.script]).replace('\n', '\n\t')

    def __repr__(self):
        out = 'Program tree:\n\t' + '\n'.join([str(i) for i in self.script]).replace('\n', '\n\t')
        out += '\nDeclarated Local Variables:\n\t' + '\n\t'.join([str(i) for i in self.vars])
        out += '\nDeclarated Functions:\n\t' + '\n\t'.join([str(i) for i in self.functions])
        return out


def _OR(first, second) -> Expression:
    if type(first) == CONST and type(second) == CONST:
        if first.type == bool and second.type == bool:
            return CONST(bool, first.val or second.val)
        elif first.type == int or second.type == int:
            raise Exception('Incorrect types.')
        else:
            return OR(first, second)
    else:
        return OR(first, second)

def _GT(first, second) -> Expression:
    if type(first) == CONST and type(second) == CONST:
        if first.type == int and second.type == int:
            return CONST(bool, first.val > second.val)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _LT(first, second) -> Expression:
    if type(first) == CONST and type(second) == CONST:
        if first.type == int and second.type == int:
            return CONST(bool, first.val < second.val)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _NOT(first) -> Expression:
    if type(first) == CONST:
        if first.type == bool:
            return CONST(bool, not first.val)
        elif first.type == int:
            raise Exception('Incorrect types.')
        else:
            return NOT(first)
    else:
        return NOT(first)

def _INC(first) -> Expression:
    if type(first) == CONST and first.type == Var:
        return INC(first)
    else:
        raise Exception('Incorrect types.')

def _DEC(first) -> Expression:
    if type(first) == CONST and first.type == Var:
        return DEC(first)
    else:
        raise Exception('Incorrect types.')

#-GRAMMAR------------------------------------------------------------

def p_prog(p):
    '''prog : prog line es
            | prog fdecl es'''
    if p[1]:
        if p[2]: 
            if type(p[2]) == list:
                p[1].script.extend(p[2])
            else:
                p[1].script.append(p[2])
        p[0] = p[1]
    else:
        if p[2]:
            if type(p[2]) == list:
                p[0] = Prog(p[2])
            else:
                p[0] = Prog([p[2]])
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
    p[0] = Assign(p[1], p[3])

def p_sent_extend(p):
    '''sent : EXTEND1 ID expr
            | EXTEND2 ID expr expr'''
    if len(p) == 5:
        p[0] = EXTEND(p[2], p[3], p[4])
    else:
        p[0] = EXTEND(p[2], p[3], None)

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
        p[0] = p[2].append([])
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]

def p_arrs_empty(p):
    '''arrs : '''
    p[0] = [[]]

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
            p[0] = CONST(int, int(p[1]))
        elif p[1] == 'TRUE' or p[1] == 'FALSE':
            if p[1] == 'TRUE': p[1] = True
            else: p[1] = False
            p[0] = CONST(bool, p[1])
        elif type(p[1]) == Oper:
            p[0] = p[1]
        else:
            p[0] = CONST(Var, p[1])
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
            p[0] = Oper('PUSH', p[1][4], None)
        elif p[1][0:3] == 'GET':
            p[0] = Oper('GET', p[1][3], None)
        elif p[1] == 'FORW' or p[1] == 'BACK' or p[1] == 'RIGHT' or p[1] == 'LEFT':
            p[0] = Oper('MOVE', p[1][0], None)
        else:
            p[0] = p[1]
    elif p[1] == 'SIZE1':
        p[0] = Oper('SIZE', p[2], None)
    elif p[1] == 'SIZE2':
        p[0] = Oper('SIZE', p[2], p[3])


def p_access(p):
    '''access : ID OPEN expr COMA expr CLOSE
              | ID OPEN expr CLOSE'''
    if len(p) == 5:
        p[0] = Brackets(p[1], p[3], None)
    else:
        p[0] = Brackets(p[1], p[3], p[5])


#-LOGIC------------------------------------------------------------

def p_logic(p):
    '''logic : cond
             | loop'''
    p[0] = p[1]

def p_cond(p):
    '''cond : IF expr sent else
            | IF expr group else'''
    if type(p[3]) != list:
        p[3] = [p[3]]
    if p[4]:
        p[0] = Condition(p[2], p[3], p[4])
    else:
        p[0] = Condition(p[2], p[3], p[4])

def p_else(p):
    '''else : ELSE sent
            | ELSE group'''
    if type(p[2]) != list:
        p[2] = [p[2]]
    p[0] = p[2]
    
def p_else_empty(p):
    '''else : '''
    p[0] = None

def p_loop(p):
    '''loop : WHILE expr DO sent
            | WHILE expr DO group'''
    if type(p[4]) != list:
        p[4] =[p[4]]
    p[0] = While(p[2], p[4])

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

def build_tree(code) -> Prog:
    return parser.parse(code)

prog = build_tree(text+'\n')

print(prog)

input_file = open('map.txt')
Map = [[j for j in i if j != '\n'] for i in input_file]

prog.execute(Map)

print(prog.__repr__())

#-------------------------------------------------------------


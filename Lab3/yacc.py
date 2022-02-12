from lex import tokens, text
import ply.yacc as yacc

maxint = 4096

class Tmp:

    def __init__(self, type: type, data):
        self.type = type
        self.data = data

class Var:

    def __init__(self, id: str, type: type, const: bool, n: int, expr, data = None) -> None:
        self.id = id
        self.type = type
        self.const = const
        self.dimensions = n
        self.expr = expr
        self.data = data

    def run_var_init(self, program, function):
        if self.expr:
            if self.dimensions == 2:
                self.data = [[get_expr(expr, self.type, program, function).data for expr in arr] for arr in self.expr]

            elif self.dimensions == 1:
                self.data = [get_expr(expr, self.type, program, function).data for expr in self.expr]
            else:
                self.data = get_expr(self.expr, self.type, program, function).data

    def check_type(self, type):
        if self.type == type:
            return True
        else:
            raise Exception('Bad type.')

    def check_dimensions(self, n):
        if self.dimensions == n:
            return True
        else:
            raise Exception('Bad type.')

    def _const(self):
        if self.const:
            raise Exception('Try to change const.')
        else:
            return False

    def copy(self):
        return Var(self.id, self.type, self.const, self.dimensions, self.expr, self.data)

    def __str__(self):
        return 'var inst, id: {}, type: {}'.format(self.id, self.type)

    def __repr__(self):
        return 'Var | ID: {} | Data: {}\t'.format(self.id, str(self.type), self.data)


class Function:
    
    def __init__(self, id, default_pars, script, default_vars) -> None:
        self.id = id
        self.vars = dict()
        self.def_pars = default_pars
        self.def_vars = default_vars
        self.script = script
        self.cur_inst = [0, 'declarating function ' + self.id]

    def run_func_init(self, program):
        for par, expr in self.def_pars:
            tmp = expr.Solve(program, None)
            self.vars[par] = Var(par, tmp.type, False, 0, None, tmp.data)
        self.def_pars = [i[0] for i in self.def_pars]

        for var, expr in self.def_vars:
            tmp = expr.Solve(program, None)
            self.vars[var] = Var(var, tmp.type, False, 0, None, tmp.data)
        self.def_vars = [i[0] for i in self.def_vars]

    def check_call(self, pars, vars, program, function):
        self.cur_inst = [0, 'calling function ' + self.id]
        if len(self.def_pars) != len(pars):
            program.set_exception('Expected {} args, but {} stated'.format(len(self.def_pars), len(pars)))
            raise Exception('Expected {} args, but {} stated'.format(len(self.def_pars), len(pars)))
        if len(self.def_vars) != len(vars):
            program.set_exception('Expected {} args, but {} stated'.format(len(self.def_pars), len(pars)))
            raise Exception('Expected {} outputs, but {} stated'.format(len(self.def_vars), len(vars)))
        for i, ident in enumerate(vars):
            if ident:
                if type(ident) == Brackets:
                    self.vars[self.def_vars[i]].check_type(ident._type(program, function))
                else: 
                    self.vars[self.def_vars[i]].check_type(get_var(ident, program, function).type)
        for i, expr in enumerate(pars):
            if expr:
                self.vars[self.def_pars[i]].check_type(expr._type(program, function))

    def duplicate(self):
        tmp = Function(self.id, [i for i in self.def_pars], self.script, [i for i in self.def_vars])
        tmp.vars = {ident:self.vars[ident].copy() for ident in self.vars}
        return tmp

    def run(self, args, program):
        for i in range(len(args)):
            if args[i]:
                self.vars[self.def_pars[i]].data = args[i]
        for i in range(len(self.script)):
            self.cur_inst = [i+1, self.script[i]]
            self.script[i].interpretate(program, self)

        return [self.vars[ident].data for ident in self.def_vars]

    def __str__(self):
        return 'function {}, in inst #{}, in {}'.format(self.id, self.cur_inst[0], self.cur_inst[1])


def get_var(ident, program, function) -> Var:
    if function:
        var = function.vars.get(ident)
        if not var:
            var = program.vars.get(ident)
    else:
        var = program.vars.get(ident)
    if not var:
        program.set_exception('Variable not declarated')
        raise Exception('Variable not declarated')
    return var

def get_decvar(ident, program, function) -> Var:
    if function:
        var = function.vars.get(ident)
        if not var:
            var = program.vars.get(ident)
    else:
        var = program.vars.get(ident)
    if not var:
        program.set_exception('Variable not declarated')
        raise Exception('Variable not declarated.')
    if var.data == None:
        program.set_exception('Variable has no data.')
        raise Exception('Variable has no data.')
    return var

def get_expr(expr, type, program, function) -> Tmp:
    tmp = expr.Solve(program, function)
    if tmp.type != type and type != None:
        program.set_exception('Expected {} type, but {} got.'.format(type, tmp.type))
        raise Exception('Expected {} type, but {} got.'.format(type, tmp.type))
    return tmp

class Expression:
    pass

class VAL(Expression):

    def __init__(self, type, val):
        self.type = type
        self.ident = val

    def __repr__(self) -> str:
        return str(self.ident)

    def Solve(self, program, function) -> Tmp:
        if self.type == Var:
            return get_decvar(self.ident, program, function)
        else:
            return Tmp(self.type, self.ident)

    def _type(self, program, function):
        if self.type == Var:
            return get_decvar(self.ident, program, function).type
        else:
            return self.type

class GT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} > {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, int, program, function)
        right = get_expr(self.right, int, program, function)
        return Tmp(bool, left.data > right.data)

    def _type(self, program=None, function=None):
        return bool

class LT(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} < {} )'.format(self.left, self.right)
    
    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, int, program, function)
        right = get_expr(self.right, int, program, function)
        return Tmp(bool, left.data < right.data)

    def _type(self, program=None, function=None):
        return bool

class OR(Expression):

    def __init__(self, first, second):
        self.left = first
        self.right = second

    def __repr__(self) -> str:
        return '( {} OR {} )'.format(self.left, self.right)

    def Solve(self, program, function) -> Tmp:
        left = get_expr(self.left, bool, program, function)
        right = get_expr(self.right, bool, program, function)
        return Tmp(bool, left.data or right.data)

    def _type(self, program=None, function=None):
        return bool

class NOT(Expression):

    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return '( NOT {} )'.format(self.val)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.val, bool, program, function)
        return Tmp(bool, not var.data)

    def _type(self, program=None, function=None):
        return bool

class INC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '++{}'.format(self.expr)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.expr, int, program, function)
        var._const()
        var.data += 1
        return Tmp(int, var.data)

    def _type(self, program=None, function=None):
        return int

class DEC(Expression):

    def __init__(self, val):
        self.expr = val

    def __repr__(self) -> str:
        return '--{}'.format(self.expr)

    def Solve(self, program, function) -> Tmp:
        var = get_expr(self.expr, int, program, function)
        var._const()
        var.data -= 1
        return Tmp(int, var.data)

    def _type(self, program=None, function=None):
        return int

class Oper(Expression):

    def __init__(self, operator, first, second):
        self.operator = operator
        self.first = first
        self.second = second

    def __repr__(self):
        return '[ {} : {} , {} ]'.format(self.operator, self.first, self.second)

    def Solve(self, program, function) -> Tmp:
        if self.operator == 'PUSH':
            type = bool
            data = program.push(self.first)
        elif self.operator == 'GET':
            type = int
            data = program.get(self.first)
        elif self.operator == 'MOVE':
            type = bool
            data = program.move(self.first)
        elif self.operator == 'SIZE':
            var = get_decvar(self.first, program, function)
            type = int
            if self.second:
                tmp = get_expr(self.second, int, program, function).data
                data = var.data[tmp]
            else:
                data = var.data
        return Tmp(type, data)

    def _type(self, program=None, function=None):
        if self.operator == 'PUSH' or self.operator == 'MOVE':
            return bool
        elif self.operator == 'GET' or self.operator == 'SIZE':
            return int

class Assign:

    def __init__(self, a, b: Expression):
        self.target = a
        self.expr = b

    def __str__(self) -> str:
        return '{} := {}'.format(self.target, self.expr)

    def run_assign(self, program, function: Function):
        tmp = self.expr.Solve(program, function)
        if type(self.target) == Brackets:
            var = self.target.Solve(program, function)
        else:
            var = get_var(self.target, program, function)
        if var.check_type(tmp.type) and not var._const():
            var.data = tmp.data

class EXTEND:
    
    def __init__(self, ident, expr1, expr2):
        self.ident = ident
        self.expr1 = expr1
        self.expr2 = expr2

    def run_extend(self, program, function: Function):
        tmp1 = get_expr(self.expr1, int, program, function).data
        if self.expr2:
            var = get_var(self.ident, program, function)
            var.check_dimensions(2)
            tmp2 = get_expr(self.expr2, int, program, function).data
            if tmp1 < len(var.data):
                if tmp2 >= len(var.data[tmp1]):
                    var.data[tmp1].extend([None for i in range(tmp2 - len(var.data[tmp1]))])
                else:
                    program.set_exception('Runtime error.')
                    raise Exception('Runtime error.')
            else:
                program.set_exception('Index out of range.')
                raise Exception('Index out of range.')
        else:
            var = get_var(self.ident, program, function)
            if var.data:
                if tmp1 >= len(var.data):
                    var.data[tmp1].extend([None for i in range(tmp1 - len(var.data))])
                else:
                    program.set_exception('Runtime error.')
                    raise Exception('Runtime error.')
            elif var.dimensions() == 2:
                var.data = [[] for i in range(tmp1)]
            elif var.dimensions() == 1:
                var.data = [None for i in range(tmp1)]

    def __str__(self):
        return 'Extend: {}[{}][{}]'.format(self.ident, self.expr1, self.expr2)

class Brackets(Expression):

    def __init__(self, ident, i, j):
        self.ident = ident
        self.expr1 = i
        self.expr2 = j

    def __str__(self):
        out = '{}[{}]'.format(self.ident, self.expr1)
        if self.expr2:
            out += '[{}]'.format(self.expr2)
        return out

    def Solve(self, program, function) -> Var:
        var = get_decvar(self.ident, program, function)
        tmp1 = get_expr(self.expr1, int, program, function).data
        if self.expr2 and var.check_dimensions(2):
            tmp2 = get_expr(self.expr2, int, program, function).data
            return var[tmp1][tmp2]
        else:
            var.check_dimensions(1)
            return var[tmp1]

    def _type(self, program, function):
        return get_decvar(self.ident, program, function).type

class Line:

    def __init__(self, statement) -> None:
        self.statement = statement

    def interpretate(self, program, function):
        line = self.statement
        if type(line) == Var:
            line.run_var_init(program, function)
            if function:
                function.vars[line.id] = line
            else:
                program.vars[line.id] = line
        elif type(line) == Function:
            if program.functions.get(line.id):
                program.set_exception('Function already declarated.')
                raise Exception('Function already declarated.')
            line.run_func_init(program)
            program.functions[line.id] = line
        elif type(line) == Condition:
            line.run_cond(program, function)
        elif type(line) == While:
            line.run_while(program, function)
        elif type(line) == Fcall:
            line.run_fcall(program, function)
        elif type(line) == Assign:
            line.run_assign(program, function)
        elif isinstance(line, Expression):
            line.Solve(program, function)
        elif type(line) == EXTEND:
            line.run_extend(program, function)
        elif type(line) == Print:
            line.execute(program, function)

    def __str__(self):
        return str(self.statement)

class Condition:
    
    def __init__(self, expr, then, _else) -> None:
        self.expr = expr
        self.then = then
        self._else = _else
        self.cur_inst = [0, self.expr]

    def run_cond(self, program, function):
        if get_expr(self.expr, bool, program, function).data:
            exe_gr = self.then
        else:
            exe_gr = self._else
        if exe_gr:
            for i in range(len(exe_gr)):
                self.cur_inst = [i+1, exe_gr[i]]
                exe_gr[i].interpretate(program, function)
    
    def __str__(self):
        return 'condition, in instance #{}; In {}'.format(self.cur_inst[0], self.cur_inst[1])

class While:
    
    def __init__(self, expr, do) -> None:
        self.expr = expr
        self.do = do
        self.cur_inst = [0, self.expr]

    def run_while(self, program, function):
        while get_expr(self.expr, bool, program, function).data:
            for i in range(len(self.do)):
                self.cur_inst = [i+1, self.do]
                self.do[i].interpretate(program, function)

    def __str__(self):
        return 'while, in inst #{}; In {}'.format(self.cur_inst[0], self.cur_inst[1])

class Vector:

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, arg):
        return Vector(self.x + arg.x, self.y + arg.y)
    
    def __iadd__(self, arg):
        self.x += arg.x
        self.y += arg.y
        return self

    def __isub__(self, arg):
        self.x -= arg.x
        self.y -= arg.y
        return self

    def __eq__(self, arg):
        return self.x == arg.x and self.y == arg.y

    def rotate(self, direction):
        x, y = self.x, self.y
        if direction == 'F':
            pass
        elif direction == 'B':
            x, y = -x, -y
        elif direction == 'R':
            x, y = -y, x
        elif direction == 'L':
            x, y = y, -x
        return Vector(x, y)

class map_container:

    def __init__(self, map: list) -> None:
        self.map = map

    def get(self, pair: Vector):
        if (pair.y < len(self.map) and pair.y >= 0) and (pair.x < len(self.map[pair.y]) and pair.x >= 0):
            return self.map[pair.y][pair.x]
        else:
            return None
    
    def __getitem__(self, pair: Vector) -> str:
        tmp = self.get(pair)
        if tmp: return tmp
        else: return '#'

    def __setitem__(self, pair: Vector, val) -> str:
        tmp = self.get(pair)
        if tmp: self.map[pair.y][pair.x] = val


class Prog:

    def __init__(self, lines):
        self.vars = dict()
        self.functions = dict()
        self.script = lines

        self.map = None
        self.cur = Vector(0, 0)
        self.direct = Vector(1, 0)
        self.exit = Vector(0, 0)
        self.undo_stack = []
        self.root = []

        self.cur_inst = [0, 'Loading map.']
        self.exception = None

    def find_exit(self, file):
        tmp = [[i for i in line if i != '\n'] for line in file]
        self.map = map_container(tmp)
        self.cur = [Vector(j, i) for i in range(len(tmp)) for j in range(len(tmp[i])) if tmp[i][j] == 'S'].pop()
        self.exit = [Vector(j, i) for i in range(len(tmp)) for j in range(len(tmp[i])) if tmp[i][j] == 'F'].pop()
        self.map[self.cur] = ' '
        self.map[self.exit] = ' '
        if not self.map:
            self.set_exception('Error in loading map.')
            raise Exception('Error in loading map.')
        self.robot_map = self.map
        for i in range(len(self.script)):
            self.cur_inst = [i+1, self.script[i]]
            self.script[i].interpretate(self, None)

    def check_func_decl(self, ident) -> Function:
        if self.functions.get(ident):
            return self.functions[ident]
        else:
            self.set_exception('Function not declarated.')
            raise Exception('Function not declarated.')

    def push(self, direction):
        self.direct = self.direct.rotate(direction)

        if self.map[self.direct + self.cur] == '#':
            if self.map[self.direct + self.direct + self.cur] == '#':
                return False
            else:
                self.map[self.direct + self.cur] = ' '
                self.map[self.direct + self.direct + self.cur] = '#'
                self.undo_stack.append([self.direct + self.cur, self.direct + self.direct + self.cur])
        self.root.append(self.cur)
        self.cur += self.direct
        if self.cur == self.exit:
            self.exception = 'Robot found root.'
            raise
        return True

    def get(self, direction):
        tmp = self.direct.rotate(direction)
        x, y = self.exit.x - self.direct.x, self.exit.y - self.direct.y
        if tmp.x == 0:
            if y*tmp.y > 0 or y == 0: return y
            else: return maxint
        else:
            if x*tmp.x > 0 or x == 0: return x
            else: return maxint

    def move(self, direction):
        self.direct = self.direct.rotate(direction)

        if self.map[self.direct + self.cur] == '#':
            return False
        self.cur += self.direct
        self.undo_stack.clear()
        self.root.append(Vector(self.cur.x, self.cur.y))
        if self.cur == self.exit:
            self.exception = 'Robot found root.'
            print('\n'.join([''.join(['*' if Vector(j, i) in self.root else self.map.map[i][j] for j in range(len(self.map.map[i]))]) for i in range(len(self.map.map))]))
            raise
        return True

    def undo(self):
        tmp = self.undo_stack.pop()
        self.map[tmp[1]] = ' '
        self.map[tmp[0]] = '#'
        self.cur -= self.direct

    def set_exception(self, text):
        self.exception = 'Exception in program instance #{}. In {}. {}'.format(self.cur_inst[0], self.cur_inst[1], text)

    def __str__(self):
        return '\n'.join([str(i) for i in self.script])

class Fcall:

    def __init__(self, ident, pars, vars):
        self.ident = ident
        self.pars = pars # [expr...]
        self.vars = vars # [id...]

    def run_fcall(self, program: Prog, function: Function):
        self.cur_inst = 'function ' + self.ident + ' not declarated'
        func = program.check_func_decl(self.ident)
        func.check_call(self.pars, self.vars, program, function)
        args = [expr.Solve(program, function).data if expr else None for expr in self.pars]
        func = func.duplicate()
        self.cur_inst = func
        res = func.run(args, program)
        for i in range(len(self.vars)):
            if self.vars[i]:
                if type(self.vars[i]) == Brackets:
                    var = self.vars[i].Solve(program, function)
                    var.data = res[i]
                else:
                    var = get_var(self.vars[i], program, function)
                    var._const()
                    var.data = res[i]

    def __str__(self):
        return 'fcall, {}'.format(self.cur_inst)

class Print:

    def __init__(self, ident) -> None:
        self.ident = ident

    def execute(self, program, function):
        print(get_var(self.ident, program, function).__repr__())


def _OR(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == bool and second.type == bool:
            return VAL(bool, first.val or second.val)
        elif first.type == int or second.type == int:
            raise Exception('Incorrect types.')
        else:
            return OR(first, second)
    else:
        return OR(first, second)

def _GT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.val > second.val)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _LT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.val < second.val)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return LT(first, second)
    else:
        return LT(first, second)

def _NOT(first) -> Expression:
    if type(first) == VAL:
        if first.type == bool:
            return VAL(bool, not first.val)
        elif first.type == int:
            raise Exception('Incorrect types.')
        else:
            return NOT(first)
    else:
        return NOT(first)

def _INC(first) -> Expression:
    if type(first) == VAL and first.type == Var:
        return INC(first)
    else:
        raise Exception('Incorrect types.')

def _DEC(first) -> Expression:
    if type(first) == VAL and first.type == Var:
        return DEC(first)
    else:
        raise Exception('Incorrect types.')

#-GRAMMAR------------------------------------------------------------

def p_prog(p):
    '''prog : prog line es'''
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
        else: p[0] = Prog([])

def p_prog_fdecl(p):
    '''prog : prog fdecl es'''
    if p[1]:
        if p[2]: 
            p[1].script.append(Line(p[2]))
        p[0] = p[1]
    elif p[2]:
            p[0] = Prog([Line(p[2])])
    else: p[0] = Prog([])
    

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
            | decl
            | cdecl'''
    p[0] = Line(p[1])

def p_line_gr(p):
    '''line : group'''

def p_line_empty(p):
    '''line : '''
    p[0] = None

def p_sent_pr(p):
    '''sent : PRINT ID'''
    p[0] = Print(p[2])

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
                p[2].extend(p[3])
            else:
                p[2].append(p[3])
            p[0] = p[2]
        else:
            if type(p[3]) == list:
                p[0] = p[3]
            else:
                p[0] = [p[3]]
    else:
        p[0] = p[2]

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
    p[0] = Var(p[2], bool, True, 0, p[4])

def p_cadecl(p):
    '''cadecl : CAVAR ID EQ expr'''
    p[0] = Var(p[2], int, True, 0, p[4])

#-VAR-DECL------------------------------------------------------------

def p_lvdecl(p):
    '''lvdecl : LVAR ID
              | LVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], bool, False, 0, p[4])
    else:
        p[0] = Var(p[2], bool, False, 0, None)

def p_avdecl(p):
    '''avdecl : AVAR ID
              | AVAR ID EQ expr'''
    if len(p) == 5:
        p[0] = Var(p[2], int, False, 0, p[4])
    else:
        p[0] = Var(p[2], int, False, 0, None)

#-ARR-DECL------------------------------------------------------------

def p_1ldecl(p):
    '''1ldecl : L1ARR ID
              | L1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], bool, False, 1, None)
    else:
        p[0] = Var(p[2], bool, False, 1, p[5])

def p_1adecl(p):
    '''1adecl : A1ARR ID
              | A1ARR ID EQ SOPEN vals SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], int, False, 1, None)
    else:
        p[0] = Var(p[2], int, False, 1, p[5])

def p_2ldecl(p):
    '''2ldecl : L2ARR ID
              | L2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], bool, False, 2, None)
    else:
        p[0] = Var(p[2], bool, False, 2, p[5])

def p_2adecl(p):
    '''2adecl : A2ARR ID
              | A2ARR ID EQ SOPEN arrs SCLOSE'''
    if len(p) == 3:
        p[0] = Var(p[2], int, False, 2, None)
    else:
        p[0] = Var(p[2], int, False, 2, p[5])

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
        p[2].append([])
        p[0] = p[2]
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
            | INCDEC expr
            | expr GTLT expr
            | expr OR expr
            | OPEN expr CLOSE'''
    if len(p) == 2:
        if type(p[1]) == Oper:
            p[0] = p[1]
        elif p[1] == 'TRUE' or p[1] == 'FALSE':
            if p[1] == 'TRUE': p[1] = True
            else: p[1] = False
            p[0] = VAL(bool, p[1])
        elif p[1].isdigit():
            p[0] = VAL(int, int(p[1]))
        else:
            p[0] = VAL(Var, p[1])
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
        if type(p[1]) == Brackets:
            p[0] = p[1]
        elif p[1][0:4] == 'PUSH':
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
        p[3] = [Line(p[3])]
    if p[4]:
        p[0] = Condition(p[2], p[3], p[4])
    else:
        p[0] = Condition(p[2], p[3], p[4])

def p_else(p):
    '''else : ELSE sent
            | ELSE group'''
    if type(p[2]) != list:
        p[2] = [Line(p[2])]
    p[0] = p[2]
    
def p_else_empty(p):
    '''else : '''
    p[0] = None

def p_loop(p):
    '''loop : WHILE expr DO sent
            | WHILE expr DO group'''
    if type(p[4]) != list:
        p[4] = [Line(p[4])]
    p[0] = While(p[2], p[4])

#-CALLS------------------------------------------------------------

def p_fcall(p):
    '''fcall : SOPEN vars SCLOSE EQ ID OPEN pars CLOSE'''
    p[0] = Fcall(p[5], p[7], p[2])

def p_vars(p):
    '''vars : ID COMA vars
            | COMA vars
            | access COMA vars
            | access
            | ID'''
    if len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 3:
        p[2].append(None)
        p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_vars_empty(p):
    '''vars : '''
    p[0] = [None]

def p_pars(p):
    '''pars : expr COMA pars
            | COMA pars
            | expr'''
    if len(p) == 4:
        p[3].append(p[1])
        p[0] = p[3]
    elif len(p) == 3:
        p[2].append(None)
        p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_pars_empty(p):
    '''pars : '''
    p[0] = [None]

#-PARSER------------------------------------------------------------

parser = yacc.yacc()

def build_tree(code) -> Prog:
    return parser.parse(code)

prog = build_tree(text+'\n')

map_file = open('map.txt')
try:
    prog.find_exit(map_file)

except Exception as e:
    print(e)
    print(prog.exception)

# try:
#     prog.find_exit(map_file)
# except Exception as e:
#     print(e)


from typing import NewType


class BinTree:

    def __init__(self, val, left, right):
        self.value = val
        self.right = right
        self.left = left

    def __str__(self):
        return '[ {} ]->({}, {})'.format(self.value.__str__(), self.left.__str__(), self.right.__str__())


class Token:

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __eq__(self, __o: object) -> bool:
        return self.is_token() and self.value == __o

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def is_literal(self):
        return self.type == 'literal'

    def is_token(self):
        return self.type == 'token'

    def is_group(self):
        return self.type == 'group_name'

    def __str__(self):
        return self.value


name = 0
def get_name():
    global name
    name += 1
    return name

class Automat:

    def __str__(self):
        return '\n'.join([self.start.__str__()] + ['{}: {}'.format(k, self.states[k]) for k in self.states] + [self.end.__str__()])


class NFA_Automat(Automat):

    def __init__(self, token):
        self.end = get_name()
        self.start = get_name()
        self.states = {self.start: {token: [self.end]}}

    def conc(self, other):
        self.states.update(other.states)
        self.states[self.end] = self.states.pop(other.start)
        self.end = other.end
        return self

    def alt(self, other):
        new_start_state = get_name()
        new_end_state = get_name()
        self.states.update(other.states)
        self.states.update({new_start_state: {'': [self.start, other.start]}, self.end: {'': [new_end_state]}, other.end: {'': [new_end_state]}})
        self.start = new_start_state
        self.end = new_end_state
        return self

    def clini(self):
        new_start_state = get_name()
        new_end_state = get_name()
        self.states[self.end] = {'': [new_end_state, self.start]}
        self.end = new_end_state
        self.states[new_start_state] = {'': [self.start, self.end]}
        self.start = new_start_state
        return self
    
    def figure_group(self, n):
        au_copy = self.copy()
        for i in range(n-1):
            self.conc(au_copy)
            au_copy = au_copy.copy()
        return self

    def possible(self):
        if '' in self.states[self.start]:
            self.states[self.start][''].append(self.end)
        else:
            self.states[self.start][''] = [self.end]
        return self

    def copy(self):
        new_states = {s: get_name() for s in self.states}
        new_states[self.end] = get_name()
        au_copy = NFA_Automat('')
        au_copy.start = new_states[self.start]
        au_copy.end = new_states[self.end]
        au_copy.states = {new_states[s1]:{a:[new_states[s2] for s2 in self.states[s1][a]] for a in self.states[s1]} for s1 in self.states}
        return au_copy
        

class DFA_Automat(Automat):

    def __init__(self, start: int, end: set, states: dict):
        self.start = start
        self.end = end
        self.states = states

    def copy(self):
        new_states = {s: get_name() for s in self.states}
        states = {new_states[s1]:{a:new_states[self.states[s1][a]] for a in self.states[s1]} for s1 in self.states}
        return DFA_Automat(new_states[self.start], {new_states[s] for s in self.end}, states)


symbols = set(['*', '|', '{', '}', '%', '(', ')', '?', '<', '>'])


def Parser(regex: str):
    tokens, i, ng = [], 0, 0

    while i < len(regex):
        if regex[i] not in symbols:
            tokens.append(Token('literal', regex[i]))
        elif regex[i] == '%':
            i += 1
            while i < len(regex) and regex[i] != '%':
                tokens.append(Token('literal', regex[i]))
                i+=1
            if i == len(regex):
                pass
        elif regex[i] == '{':
            j = i + 1
            while j < len(regex) and regex[j].isdigit():
                j += 1
            if j != len(regex) and regex[j] == '}' and i != j+1:
                tokens.append(Token('token', int(regex[i+1:j])))
                i = j
            else:
                pass
        elif regex[i] == '(':
            tokens.append(Token('token', regex[i]))
            gname = None
            if i+1 < len(regex):
                if regex[i+1] == '<':
                    j = i+2
                    while j < len(regex)  and regex[j] != '>':
                        if not (regex[j].isalpha() or regex[j].isdigit()):
                            pass
                        j += 1
                    if j != len(regex):
                        gname = regex[i+2:j]
                    else:
                        pass
            else:
                pass
            tokens.append(Token('group_name', [ng, gname]))
            ng += 1
        elif regex[i] == '*' or regex[i] == '|' or regex[i] == '?' or regex[i] == ')':
            tokens.append(Token('token', regex[i]))
        else:
            pass
        i += 1
    return tokens

    
def find_pair(tokens: list):
    first, last = -1, -1

    for i in range(len(tokens)):
        if tokens[i] == '(':
            first = i
        if tokens[i] == ')':
            last = i
            break

    return first, last


def tree_builder(tokens: list):
    first, last = find_pair(tokens)

    while len(tokens) > 1:
        if type(tokens[first+2]) == BinTree or tokens[first+2].is_literal():
            groot = tokens[first+2]
            parent = None
        elif last > first + 2:
            groot = BinTree(tokens[first+2], None, None)
            parent = groot
        else:
            groot = None
        for i in range(first + 3, last):
            if type(tokens[i]) == BinTree or tokens[i].is_literal():
                if parent:
                    if parent.right:
                        parent.right = BinTree(Token('token', '.'), parent.right, tokens[i])
                        parent = parent.right
                    else:
                        parent.right = tokens[i]
                else:
                    parent = BinTree(Token('token', '.'), groot, tokens[i])
                    groot = parent

            elif tokens[i] == '|':
                groot = BinTree(tokens[i], groot, None)
                parent = groot

            elif tokens[i] == '*' or tokens[i] == '?' or type(tokens[i].value) == int:
                if parent:
                    if parent.right:
                        parent.right = BinTree(tokens[i], parent.right, None)
                    else:
                        pass
                else:
                    groot = BinTree(tokens[i], groot, None)

        groot = BinTree(tokens[first+1], groot, None)
        tokens = tokens[:first] + [groot] + tokens[last+1:]
        first, last = find_pair(tokens)
        if first == -1 ^ last == -1:
            pass

    return tokens[0]


def NFA_builder(node) -> NFA_Automat:
    if type(node) == Token:
        return NFA_Automat(node.value)
    elif node == None:
        return NFA_Automat('')
    else:
        first = NFA_builder(node.left)
        if node.value == '.':
            second = NFA_builder(node.right)
            first.conc(second)
        elif node.value == '|':
            second = NFA_builder(node.right)
            first.alt(second)
        elif node.value == '*':
            first.clini()
        elif node.value == '?':
            first.possible()
        elif type(node.value.value) == int:
            first.figure_group(node.value.value)
        return first


def epsilon(nfa: NFA_Automat, state) -> frozenset:
    res = set([state])
    if nfa.states.get(state) and nfa.states[state].get(''):
        for s in nfa.states[state]['']:
            res.update(epsilon(nfa, s))
    return frozenset(res)


def DFA_builder(nfa: NFA_Automat, ABC: str) -> DFA_Automat:
    start_state = epsilon(nfa, nfa.start)
    gen_states = [start_state]
    dfa_states = {start_state: {}}
    end_states = []
    i = 0
    while i < len(gen_states):
        for a in ABC:
            next_state = set()
            for state1 in gen_states[i]:
                if nfa.states.get(state1) and nfa.states[state1].get(a):
                    for state2 in nfa.states[state1][a]:
                        next_state.update(epsilon(nfa, state2))
            next_state = frozenset(next_state)
            if len(next_state) > 0:
                if next_state not in dfa_states:
                    dfa_states[next_state] = {}
                    gen_states.append(next_state)
                dfa_states[gen_states[i]][a] = next_state
            if nfa.end in gen_states[i]:
                end_states.append(i)
        i+=1

    new_states = {s: get_name() for s in dfa_states}
    states = {new_states[s1]:{a:new_states[dfa_states[s1][a]] for a in dfa_states[s1]} for s1 in dfa_states}

    return DFA_Automat(new_states[gen_states[0]], set([new_states[gen_states[end_states[n]]] for n in range(len(end_states))]), states)


def check_equivalance(state1: int, state2: int, dfa: DFA_Automat, group_map: dict, ABC):

    for a in ABC:
        if group_map.get(dfa.states[state1].get(a)) != group_map.get(dfa.states[state2].get(a)):
            return False
    return True


def min_DFA(dfa: DFA_Automat, ABC) -> DFA_Automat:
    groups, identifier = set([frozenset(dfa.end)]), {}
    S_F = [i for i in dfa.states if i not in dfa.end]
    if S_F:
        groups.add(frozenset(S_F))
    while True:
        for raw in enumerate(groups):
            identifier.update({s:raw[0] for s in raw[1]})
        new_groups = set()
        for g in groups:
            equivalent_pairs, solo = [], []
            for state1 in g:
                for state2 in g:
                    pair = frozenset([state1, state2])
                    if check_equivalance(state1, state2, dfa, identifier, ABC):
                        if state1 != state2 and pair not in equivalent_pairs:
                            equivalent_pairs.append(pair)
                        elif pair not in solo:
                            solo.append(pair)
                        
            used_states = set()
            while len(equivalent_pairs) > 0:
                pair1 = equivalent_pairs.pop()
                tmp = set(pair1)
                j = 0
                while j < len(equivalent_pairs):
                    if pair1&equivalent_pairs[j]:
                        tmp.update(equivalent_pairs.pop(j))
                    else:
                        j += 1
                used_states.update(tmp)
                new_groups.add(frozenset(tmp))
            new_groups.update([s for s in solo if not s&used_states])

        if groups == new_groups:
            break
        groups = new_groups

    groups = {s: {} for s in groups}
    for gr in groups:
        for a in ABC:
            s1 = next(iter(gr))
            if dfa.states[s1].get(a):
                groups[gr][a] = [gr2 for gr2 in groups if dfa.states[s1].get(a) in gr2].pop()
        
    end = set([i for i in groups if i&dfa.end])
    start = [i for i in groups if dfa.start in i].pop()
    new_states = {s: get_name() for s in groups}
    states = {new_states[s]:{a:new_states[groups[s][a]] for a in groups[s]} for s in groups}

    return DFA_Automat(new_states[start], set([new_states[s] for s in end]), states)


def min_DFA2(dfa: DFA_Automat, ABC) -> DFA_Automat:
    groups, group_map = set([frozenset(dfa.end)]), dict()
    S_F = [i for i in dfa.states if i not in dfa.end]
    if S_F:
        groups.add(frozenset(S_F))
    new_groups = set()
    while groups != new_groups:
        if len(new_groups):
            groups = new_groups
        for raw in enumerate(groups):
            group_map.update({s:raw[0] for s in raw[1]})
        new_groups = set()
        for g in groups:
            used_states = set()
            for state1 in g:
                if state1 not in used_states:
                    eq_states = set([state1])
                    used_states.add(state1)
                    for state2 in g:
                        if state2 not in used_states and check_equivalance(state1, state2, dfa, group_map, ABC):
                            eq_states.add(state2)
                            used_states.add(state2)
                    new_groups.add(frozenset(eq_states))

    groups = {s: {} for s in groups}
    for gr in groups:
        for a in ABC:
            s1 = next(iter(gr))
            if dfa.states[s1].get(a):
                groups[gr][a] = [gr2 for gr2 in groups if dfa.states[s1].get(a) in gr2].pop()
        
    end = set([i for i in groups if i&dfa.end])
    start = [i for i in groups if dfa.start in i].pop()
    new_states = {s: get_name() for s in groups}
    states = {new_states[s]:{a:new_states[groups[s][a]] for a in groups[s]} for s in groups}

    return DFA_Automat(new_states[start], set([new_states[s] for s in end]), states)


def DFA_passage(dfa: DFA_Automat, string: str):
    i = 0
    state = dfa.start
    while len(string) > i and dfa.states[state].get(string[i]):
        state = dfa.states[state].get(string[i])
        i += 1
    if state in dfa.end:
        return i
    else:
        return 0


def Tree_passage(node: BinTree, string: str, i: int) -> set:
    next_pos = set()
           
    if node == None:
        if len(string) == i:
            next_pos.add(i)
    
    elif type(node) == Token:
        if i < len(string) and string[i] == node.value:
            next_pos.add(i+1)

    else:
        tmp = Tree_passage(node.left, string, i)
        if node.value == '.':
            for pos in tmp:
                next_pos.update(Tree_passage(node.right, string, pos))

        elif node.value == '|':
            next_pos.update(tmp)
            next_pos.update(Tree_passage(node.right, string, i))

        elif node.value == '*':
            s = tmp
            while len(s) != 0:
                next_pos.update(s)
                tmp = s
                s = set()
                [s.update(Tree_passage(node.left, string, pos)) for pos in tmp]
            next_pos.add(i)

        elif node.value == '?':
            next_pos.update(tmp)
            next_pos.add(i)

        elif type(node.value.value) == int:
            s = tmp
            j = 1
            while len(s) != 0 and j != node.value.value:
                tmp = s
                s = set()
                [s.update(Tree_passage(node.left, string, pos)) for pos in tmp]
                j += 1
            next_pos.update(s)
        elif node.value.is_group():
            next_pos.update(tmp)

    return next_pos


class gr_struct:

    def __init__(self, start: int, gruop_number: int, next: list=[]):
        self.start = start
        self.gnum = gruop_number
        self.next = next


class gr_generator:

    def __init__(self, string, tree):
        self.string = string
        self.tree = tree
        self.cur = tree

    def default_passage(self, i: int) -> set:
        next_pos = set()
            
        if self.cur == None:
            if len(self.string) == i:
                next_pos.add(i)

        elif type(self.cur) == Token:
            if i < len(self.string) and self.string[i] == self.cur.value:
                next_pos.add(i+1)

        else:
            cur = self.cur
            self.cur = cur.left
            tmp = self.passage(i)
            if cur.value == '.':
                self.cur = cur.right
                for pos in tmp:
                    next_pos.update(self.passage(pos))

            elif cur.value == '|':
                next_pos.update(tmp)
                self.cur = cur.right
                next_pos.update(self.passage(i))

            elif cur.value == '*':
                s = tmp
                while len(s) != 0:
                    next_pos.update(s)
                    tmp = s
                    s = set()
                    [s.update(self.passage(pos)) for pos in tmp]
                next_pos.add(i)

            elif cur.value == '?':
                next_pos.update(tmp)
                next_pos.add(i)

            elif type(self.cur.value.value) == int:
                s = tmp
                j = 1
                while len(s) != 0 and j != cur.value.value:
                    tmp = s
                    s = set()
                    [s.update(self.passage(pos)) for pos in tmp]
                    j += 1
                next_pos.update(s)
            elif cur.value.is_group():
                next_pos.update(tmp)
            self.cur = cur

        return next_pos

    
    def group_passage(self, i):
        cur = self.cur
        if cur.value.is_group():

            pass


def inversion(dfa: DFA_Automat, ABC) -> DFA_Automat:
    new_names = {s : get_name() for s in dfa.states}
    start_state = get_name()
    states = {new_names[s] : {} for s in dfa.states}
    states[start_state] = {'': [new_names[s] for s in dfa.end]}
    for state in dfa.states:
        for a in dfa.states[state]:
            dest_state = new_names[dfa.states[state][a]]
            if a in states[dest_state]:
                states[dest_state][a].append(new_names[state])
            else:
                states[dest_state][a] = [new_names[state]]
    
    nfa = NFA_Automat('')
    nfa.start = start_state
    nfa.end = new_names[dfa.start]
    nfa.states = states
    inv_dfa = DFA_builder(nfa, ABC)
    inv_dfa = min_DFA2(inv_dfa, ABC)

    return inv_dfa


def addition(dfa: DFA_Automat, ABC) -> DFA_Automat:
    new_names = {s : get_name() for s in dfa.states}
    end_state = get_name()
    states = {end_state: {a : end_state for a in ABC}}
    for state in dfa.states:
        states[new_names[state]] = {}
        for a in ABC:
            if a in dfa.states[state]:
                states[new_names[state]][a] = new_names[dfa.states[state][a]]
            else:
                states[new_names[state]][a] = end_state
    
    return DFA_Automat(new_names[dfa.start], set([end_state]), states)


def gen_regex(dfa: DFA_Automat, state) -> str:
    middle = []
    outer_states = {}
    for a in dfa.states[state]:
        if dfa.states[state][a] == state:
            middle.append(a)
        else:
            if dfa.states[state][a] not in outer_states:
                outer_states[dfa.states[state][a]] = [a]
            else:
                outer_states[dfa.states[state][a]].append(a)
    
    if len(middle) > 0:
        if len(middle) == 1 and len(middle[0]) == 1:
            regex = middle[0] + '*'
        else:
            regex = '(' + '|'.join(middle) + ')*'
    else:
        regex = ''

    end = []
    for s in outer_states:
        tmp = gen_regex(dfa, s)
        if tmp != '' and len(outer_states[s]) > 1:
            end.append('(' + '|'.join(outer_states[s]) + ')' + tmp)
        else:
            end.append('|'.join(outer_states[s]) + tmp)
            
    if state in dfa.end:
        if len(end) > 0:
            if len(end) == 1 and len(end[0]) == 1:
                regex += end[0] + '?'
            else:
                regex += '(' + '|'.join(end) + ')?'
    else:
        regex += '|'.join(end)

    return regex


def restore(dfa: DFA_Automat) -> str:
    dfa = dfa.copy()
    print(dfa)
    states = [s for s in dfa.states if not s in dfa.end and s != dfa.start]

    for s1 in states:

        Enter_states = {}
        for s2 in dfa.states:
            for a in dfa.states[s2]:
                if dfa.states[s2][a] == s1 and s2 != s1:
                    if s2 in Enter_states:
                        Enter_states[s2].append(a)
                    else:
                        Enter_states[s2] = [a]

        middle = [a for a in dfa.states[s1] if dfa.states[s1][a] == s1]
        if len(middle) > 0:
            if len(middle) == 1 and len(middle[0]) == 1:
                middle = middle[0] + '*'
            else:
                middle = '(' + '|'.join(middle) + ')*'
        else:
            middle = ''

        outer_states = {a:dfa.states[s1][a] for a in dfa.states[s1] if dfa.states[s1][a] != s1}

        for s in Enter_states:
            for a1 in Enter_states[s]:
                dfa.states[s].pop(a1)
                for a2 in outer_states:
                    dfa.states[s][a1 + middle + a2] = outer_states[a2]
        dfa.states.pop(s1)
    print(dfa)

    return gen_regex(dfa, dfa.start)


'a(s{2}da)?a|ds*'
'aa|ds*|sa?'
'ds*sss(s|sa?)sd'
'ds*|da|db|ccb*dd|ccd'
regex = 'd(s*)sss'
regex = '(' + regex + ')'
tokens = Parser(regex)
tree = tree_builder(tokens)
print(tree)

ABC = 'asdbc'

NFA = NFA_builder(tree)
print(NFA)
DFA = DFA_builder(NFA, ABC)
print(DFA)
min = min_DFA2(DFA, ABC)
print(min)
print('----------------------------------------------------------------------------')
s = 'dssss'
print(Tree_passage(tree, s, 0))
print(Tree_passage(tree, s, 0))
print('----------------------------------------------------------------------------')
print(addition(min, ABC))
print(inversion(min, ABC))
print(restore(min))
print('----------------------------------------------------------------------------')
gr = gr_generator(s, tree)
print(gr.passage(0))
print(gr.sgroups)
print(gr.egroups)
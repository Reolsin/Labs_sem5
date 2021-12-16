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

    def __str__(self):
        return self.value


name = 0
def get_name():
    global name
    name += 1
    return name

class Automat:

    def __str__(self):
        return '\n'.join([str(self.start)] + ['{}: {}'.format(k, self.states[k]) for k in self.states] + [str(self.end)])


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


symbols = set(['*', '|', '{', '}', '%', '(', ')', '?', '<', '>'])


def Parser(regex: str):
    tokens, i = [], 0

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
                        if not (regex[j].isalpha() or regex[j].isdigit() or regex[j] == '_'):
                            pass
                        j += 1
                    if j != len(regex):
                        gname = regex[i+2:j]
                    else:
                        pass
            else:
                pass
            tokens.append(Token('group_name', gname))
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
            pass
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


# def min_DFA(dfa: DFA_Automat) -> DFA_Automat:
#     groups, identifier = set([frozenset(dfa.end)]), {}
#     S_F = [i for i in dfa.states if i not in dfa.end]
#     if S_F:
#         groups.add(frozenset(S_F))
#     while True:
#         for raw in enumerate(groups):
#             identifier.update({s:raw[0] for s in raw[1]})
#         new_groups = set()
#         for g in groups:
#             equivalent_pairs, solo = [], []
#             for state1 in g:
#                 for state2 in g:
#                     pair = frozenset([state1, state2])
#                     for a in ABC:
#                         if identifier.get(dfa.states[state1].get(a)) != identifier.get(dfa.states[state2].get(a)):
#                             pair = None
#                             break
#                     if pair and state1 != state2 and pair not in equivalent_pairs:
#                         equivalent_pairs.append(pair)
#                     elif pair and pair not in solo:
#                         solo.append(pair)
                        
#             used_states = set()
#             while len(equivalent_pairs) > 0:
#                 pair1 = equivalent_pairs.pop()
#                 tmp = set(pair1)
#                 j = 0
#                 while j < len(equivalent_pairs):
#                     if pair1&equivalent_pairs[j]:
#                         tmp.update(equivalent_pairs.pop(j))
#                     else:
#                         j += 1
#                 used_states.update(tmp)
#                 new_groups.add(frozenset(tmp))
#             new_groups.update([s for s in solo if not s&used_states])

#         if groups == new_groups:
#             break
#         groups = new_groups


#     groups = {s: {} for s in groups}
#     for gr in groups:
#         for a in ABC:
#             s1 = next(iter(gr))
#             if dfa.states[s1].get(a):
#                 groups[gr][a] = [gr2 for gr2 in groups if dfa.states[s1].get(a) in gr2].pop()
        
#     end = set([i for i in groups if i&dfa.end])
#     start = [i for i in groups if dfa.start in i].pop()
#     new_states = {s: get_name() for s in groups}
#     states = {new_states[s]:{a:new_states[groups[s][a]] for a in groups[s]} for s in groups}

#     return DFA_Automat(new_states[start], set([new_states[s] for s in end]), states)



def check_equivalance(state1: int, state2: int, dfa: DFA_Automat, group_map: dict, ABC):

    for a in ABC:
        if group_map.get(dfa.states[state1].get(a)) != group_map.get(dfa.states[state2].get(a)):
            return False
    return True


def min_DFA2(dfa: DFA_Automat, ABC) -> DFA_Automat:
    groups, group_map = set([frozenset(dfa.end)]), dict()
    S_F = [i for i in dfa.states if i not in dfa.end]
    if S_F:
        groups.add(frozenset(S_F))
    new_groups = set()
    while groups != new_groups:
        for raw in enumerate(groups):
            group_map.update({s:raw[0] for s in raw[1]})
        if len(new_groups):
            groups = new_groups
        new_groups = set()
        for g in groups:
            used_states = set()
            for state1 in g:
                if state1 not in used_states:
                    eq_states = set([state1])
                    used_states.add(state1)
                    for state2 in g - used_states:
                        if check_equivalance(state1, state2, dfa, group_map, ABC):
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


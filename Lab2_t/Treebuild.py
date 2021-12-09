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
        return self.type == 'token' and self.value == __o

    def __ne__(self, __o: object) -> bool:
        return self.type != 'token' or self.value != __o

    def is_literal(self):
        return self.type == 'literal'

    def is_token(self):
        return self.type == 'token'

    def __str__(self):
        return self.value


class State:

    def __init__(self, name, relations: dict):
        self.name = name
        self.relations = relations

name = 0
def get_name():
    global name
    tmp = name
    name += 1
    return tmp

class Automat:

    def __str__(self):
        return '\n'.join([str(self.start)] + ['{}: {}'.format(k, self.states[k]) for k in self.states] + [str(self.end)])

class NFA_Automat(Automat):

    def __init__(self, start: int, relation: dict, end: int):
        self.states = {start: relation}
        self.start = start
        self.end = end

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
        self.states[self.start][''].append(self.end)
        return self

    def copy(self):
        new_states = {s: get_name() for s in self.states}
        new_states[self.end] = get_name()
        au_copy = NFA_Automat(new_states[self.start], {}, new_states[self.end])
        au_copy.states = {new_states[s1]:{a:[new_states[s2] for s2 in self.states[s1][a]] for a in self.states[s1]} for s1 in self.states}
        return au_copy
        

class DFA_Automat(Automat):

    def __init__(self, start: int, end: set, states: dict):
        self.start = start
        self.end = end
        self.states = states


symbols = set(['*', '|', '{', '}', '%', '(', ')', '?', '<', '>'])
ABC = 'asd'

def Parser(regex):
    tokens = []
    i = 0

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
        elif regex[i] == '(' or regex[i] == ')' or regex[i] == '*' or regex[i] == '|' or regex[i] == '?':
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
        if type(tokens[first+1]) or tokens[first+1].is_literal():
            groot = tokens[first+1]
            parent = None
        else:
            groot = BinTree(tokens[first+1], None, None)
            parent = groot

        for i in range(first + 2, last):
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
                    groot = BinTree(tokens[i], groot, None)

        tokens = tokens[:first] + [groot] + tokens[last+1:]
        first, last = find_pair(tokens)

    return tokens[0]


def leaf_automat(token) -> NFA_Automat:
    end = get_name()
    return NFA_Automat(get_name(), {token : [end]}, end)


def NFA_builder(node) -> NFA_Automat:
    if type(node) == Token:
        return leaf_automat(node.value)
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


def DFA_builder(nfa: NFA_Automat) -> DFA_Automat:
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


def min_DFA(dfa: DFA_Automat) -> DFA_Automat:
    groups = set([frozenset(dfa.end)])
    identifier = {s:0 for s in dfa.states if s in dfa.end}
    S_F = [i for i in dfa.states if i not in dfa.end]
    if S_F:
        groups.add(frozenset(S_F))
        identifier.update({s:1 for s in dfa.states if s not in dfa.end})
    new_groups = set()
    while True:
        for g in groups:
            equivalent_pairs = []
            solo = []
            for state1 in g:
                for state2 in g:
                    pair = frozenset([state1, state2])
                    for a in ABC:
                        if identifier.get(dfa.states[state1].get(a)) != identifier.get(dfa.states[state2].get(a)):
                            pair = None
                            break
                    if pair and pair not in equivalent_pairs:
                        if state1 != state2:
                            equivalent_pairs.append(pair)
                        else:
                            solo.append(pair)
            i, j = 0, 0
            while i < len(equivalent_pairs):
                pair1 = equivalent_pairs.pop(i)
                tmp = set(pair1)
                while j < len(equivalent_pairs):
                    if pair1&equivalent_pairs[j]:
                        tmp.update(equivalent_pairs.pop(j))
                    else:
                        j += 1
                new_groups.add(frozenset(tmp))
            tmp = set()
            [tmp.update(g) for g in new_groups]
            new_groups.update([s for s in solo if not s&tmp])
                
        if groups == new_groups:
            break
        groups = new_groups
        for raw in enumerate(groups):
            identifier.update({s:raw[0] for s in raw[1]})

    groups = {s: {} for s in groups}
    for gr in groups:
        groups[gr] = {}
        for a in ABC:
            s1 = next(iter(gr))
            if dfa.states[s1].get(a):
                groups[gr][a] = [gr2 for gr2 in groups if dfa.states[s1].get(a) in gr2].pop()
        
    end = set([i for i in groups if i&dfa.end])
    start = [i for i in groups if dfa.start in i].pop()
    new_states = {s: get_name() for s in groups}
    states = {new_states[s]:{a:new_states[groups[s][a]] for a in groups[s]} for s in groups}

    return DFA_Automat(new_states[start], set([new_states[s] for s in end]), states)
                    


regex = 'a|ds*'
regex = '(' + regex + ')'
tokens = Parser(regex)
tree = tree_builder(tokens)

print('Tree:', tree)

NFA = NFA_builder(tree)
print(NFA)

DFA = DFA_builder(NFA)
print(DFA)

minDFA = min_DFA(DFA)
print(minDFA)

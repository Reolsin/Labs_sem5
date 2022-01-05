from TreenParser import *


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

    def copy(self, new_names=True):
        if new_names:
            new_states = {s: get_name() for s in self.states}
            states = {new_states[s1]:{a:new_states[self.states[s1][a]] for a in self.states[s1]} for s1 in self.states}
            start_state = new_states[self.start]
            end_states = {new_states[s] for s in self.end}
        else:
            states = {s1:{a:self.states[s1][a] for a in self.states[s1]} for s1 in self.states}
            start_state = self.start
            end_states = {s for s in self.end}

        return DFA_Automat(start_state, end_states, states)


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


# def epsilon(nfa: NFA_Automat, state) -> frozenset:
#     res = set([state])
#     if nfa.states.get(state) and nfa.states[state].get(''):
#         for s in nfa.states[state]['']:
#             res.update(epsilon(nfa, s))
#     return frozenset(res)


def epsilon(nfa: NFA_Automat, state) -> frozenset:
    res = set([state])
    next_states = set([state])
    prev_len = 0

    while len(res) != prev_len:
        prev_len = len(res)
        tmp = next_states
        next_states = set()
        [next_states.update(nfa.states[s].get('')) for s in tmp if s != nfa.end and nfa.states[s].get('')]
        res.update(next_states)

    res.discard(None)
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
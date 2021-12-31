from Authomat import *

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
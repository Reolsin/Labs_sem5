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


def addition(dfa: DFA_Automat, ABC, oldABC) -> DFA_Automat:
    if len(dfa.end) == 1 and dfa.start == next(iter(dfa.end)) and ABC == oldABC:
        return None
    new_names = {s : get_name() for s in dfa.states}
    end_state = get_name()
    end_states = set([end_state])
    states = {end_state: {a : end_state for a in ABC}}
    for state in dfa.states:
        states[new_names[state]] = {}
        if state not in dfa.end:
            end_states.add(new_names[state])
        for a in ABC:
            if a in dfa.states[state]:
                states[new_names[state]][a] = new_names[dfa.states[state][a]]
            else:
                states[new_names[state]][a] = end_state
    
    return DFA_Automat(new_names[dfa.start], end_states, states)


# def gen_regex(dfa: DFA_Automat, state) -> str:
#     middle = []
#     outer_states = {}
#     for a in dfa.states[state]:
#         if dfa.states[state][a] == state:
#             middle.append(a)
#         else:
#             if dfa.states[state][a] not in outer_states:
#                 outer_states[dfa.states[state][a]] = [a]
#             else:
#                 outer_states[dfa.states[state][a]].append(a)
    
#     if len(middle) > 0:
#         if len(middle) == 1 and len(middle[0]) == 1:
#             regex = middle[0] + '*'
#         else:
#             regex = '(' + '|'.join(middle) + ')*'
#     else:
#         regex = ''

#     end = []
#     for s in outer_states:
#         tmp = gen_regex(dfa, s)
#         if tmp != '' and len(outer_states[s]) > 1:
#             end.append('(' + '|'.join(outer_states[s]) + ')' + tmp)
#         else:
#             end.append('|'.join(outer_states[s]) + tmp)
            
#     if state in dfa.end:
#         if len(end) > 0:
#             if len(end) == 1 and len(end[0]) == 1:
#                 regex += end[0] + '?'
#             else:
#                 regex += '(' + '|'.join(end) + ')?'
#     else:
#         regex += '|'.join(end)

#     return regex


def gen_regex(l: list, postfix = '') -> str:

    if len(l) > 0:
        if len(l) == 1 and len(l[0]) == 1:
            l = l[0] + postfix
        else:
            l = '(' + '|'.join(l) + ')' + postfix
    else:
        l = ''

    return l



def restore(dfa_source: DFA_Automat) -> str:
    regex = []
    for end_state in dfa_source.end:
        dfa = dfa_source.copy(False)
        states = [s for s in dfa.states if s != end_state and s != dfa.start]

        for s1 in states:

            Enter_states = {}
            for s2 in dfa.states:
                if s1 != s2:
                    for a in dfa.states[s2]:
                        if dfa.states[s2][a] == s1:
                            if s2 in Enter_states:
                                Enter_states[s2].append(a)
                            else:
                                Enter_states[s2] = [a]

            middle = gen_regex([a for a in dfa.states[s1] if dfa.states[s1][a] == s1], '*')

            outer_states = {a:dfa.states[s1][a] for a in dfa.states[s1] if dfa.states[s1][a] != s1}

            for s in Enter_states:
                for a1 in Enter_states[s]:
                    dfa.states[s].pop(a1)
                    for a2 in outer_states:
                        dfa.states[s][a1 + middle + a2] = outer_states[a2]
            dfa.states.pop(s1)
        
        if len(dfa.states) == 1:
            r = gen_regex([a for a in dfa.states[dfa.start]], '*')
        else:
            mid_start = gen_regex([a for a in dfa.states[dfa.start] if dfa.states[dfa.start][a] == dfa.start], '*')
            mid_end = gen_regex([a for a in dfa.states[end_state] if dfa.states[end_state][a] == end_state], '*')
            start_end = gen_regex([a for a in dfa.states[dfa.start] if dfa.states[dfa.start][a] == end_state], '')
            end_start = gen_regex([a for a in dfa.states[end_state] if dfa.states[end_state][a] == dfa.start], '')
            if len(end_start) > 0:
                r = mid_start + start_end + mid_end + '(' + end_start + mid_start + start_end + mid_end + ')*'
            else:
                r = mid_start + start_end + mid_end
        regex.append(r)

    return '|'.join(regex)
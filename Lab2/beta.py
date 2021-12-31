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
from Operations import *


class regex:

    def __init__(self, regex: str):
        self.regex = regex
        tmp, self.ABC = Parser(regex)
        self.tree = tree_builder(tmp)


    def tree_match(self, string: str):
        self.string = string
        self.cur = self.tree
        return self.tree_passage(0)


    def tree_passage(self, i: int) -> set:
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
    
    def dfa_passage(self, string: str):
        i = 0
        state = self.dfa.start
        while len(string) > i and self.dfa.states[state].get(string[i]):
            state = self.dfa.states[state].get(string[i])
            i += 1
        if state in self.dfa.end:
            return i
        else:
            return 0


    def compile(self):
        self.dfa = DFA_builder(NFA_builder(self.tree), self.ABC)
        self.dfa = min_DFA2(self.dfa, self.ABC)

    def inversion(self):
        new = regex('')
        new.regex = self.regex
        new.tree = self.tree
        new.ABC = self.ABC
        new.dfa = inversion(self.dfa, new.ABC)
        return new

    def addition(self, new_symbols: set=set()):
        new = regex('')
        new.regex = self.regex
        new.tree = self.tree
        new.ABC = self.ABC
        new.ABC.update(new_symbols)
        new.dfa = addition(self.dfa, new.ABC)
        return new

    def restore(self):
        return restore(self.dfa)


'a(s{2}da)?a|ds*'
'aa|ds*|sa?'
'ds*sss(s|sa?)sd'
'ds*|da|db|ccb*dd|ccd'
regx = 'd(s*)sss'
regx = '(' + regx + ')'
# tokens, ABC = Parser(regx)
# tree = tree_builder(tokens)
# print(tree)
# print('----------------------------------------------------------------------------')
# NFA = NFA_builder(tree)
# print(NFA)
# DFA = DFA_builder(NFA, ABC)
# print(DFA)
# min = min_DFA2(DFA, ABC)
# print(min)
# print('----------------------------------------------------------------------------')
# print(addition(min, ABC))
# print(inversion(min, ABC))
# print(restore(min))
# print('----------------------------------------------------------------------------')
s = 'dssss'
gr = regex(regx)

print(gr.tree_match(s))
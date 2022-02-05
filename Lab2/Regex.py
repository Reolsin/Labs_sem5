from Operations import *


class regex:

    def __init__(self, regex: str):
        self.regex = regex
        tmp, self.ABC = Parser(regex)
        self.tree = tree_builder(tmp)
        self.dfa = None
        self.res = None


    def tree_match(self, string: str):
        if self.tree:
            self.string = string
            self.cur = self.tree
            return self.tree_passage(0)
        else:
            raise Exception('This regex object only has dfa inside.')


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
            tmp = self.tree_passage(i)
            if cur.value == '.':
                self.cur = cur.right
                for pos in tmp:
                    next_pos.update(self.tree_passage(pos))

            elif cur.value == '|':
                next_pos.update(tmp)
                self.cur = cur.right
                next_pos.update(self.tree_passage(i))

            elif cur.value == '*':
                s = tmp
                while len(s) != 0:
                    next_pos.update(s)
                    tmp = s
                    s = set()
                    [s.update(self.tree_passage(pos)) for pos in tmp]
                next_pos.add(i)

            elif cur.value == '?':
                next_pos.update(tmp)
                next_pos.add(i)

            elif type(cur.value.value) == int:
                s = tmp
                j = 1
                while len(s) != 0 and j != cur.value.value:
                    tmp = s
                    s = set()
                    [s.update(self.tree_passage(pos)) for pos in tmp]
                    j += 1
                next_pos.update(s)
            elif cur.value.is_group():
                next_pos.update(tmp)
            self.cur = cur

        return next_pos
    
    def dfa_passage(self, string: str):
        self.string = string
        if self.dfa:
            i = 0
            state = self.dfa.start
            while len(string) > i and self.dfa.states[state].get(string[i]):
                state = self.dfa.states[state].get(string[i])
                i += 1
            if state in self.dfa.end:
                return i
            else:
                return 0
        else:
            raise Exception('Call the compile function before using dfa methods.')


    def compile(self):
        self.dfa = DFA_builder(NFA_builder(self.tree), self.ABC)
        self.dfa = min_DFA2(self.dfa, self.ABC)

    def inversion(self):
        if self.dfa:
            new = regex('()')
            new.ABC = self.ABC
            new.dfa = inversion(self.dfa, new.ABC)
            new.regex = new.restore()
            new.tree = None
            return new
        else:
            raise Exception('Call the compile function before using dfa methods.')

    def addition(self, new_symbols: set=set()):
        if self.dfa:
            new = regex('()')
            new.ABC = set()
            new.ABC.update(self.ABC)
            new.ABC.update(new_symbols)
            new.dfa = addition(self.dfa, new.ABC, self.ABC)
            if new.dfa:
                new.regex = new.restore()
                new.tree = None
                return new
            else:
                return None
        else:
            raise Exception('Call the compile function before using dfa methods.')

    def restore(self):
        if self.dfa:
            if not self.res:
                self.res = restore(self.dfa)
            return self.res            
        else:
            raise Exception('Call the compile function before using dfa methods.')


'a(s{2}da)?a|ds*'
'aa|ds*|sa?'
'ds*sss(s|sa?)sd'
'ds*|da|db|ccb*dd|ccd'
'((a|bd*c)*bd*|a*)*'
'((a)*)*'
'(a|bd*c)*bd*|(a|bd*c)*'
regx = 'ds*'
regx = '(' + regx + ')'
tokens, ABC = Parser(regx)
tree = tree_builder(tokens)
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
source = regex(regx)
source.compile()

inv = source.inversion()
add = source.addition(set(['d']))

print('Regex: ', source.regex)
print('Tree: ', source.tree)
print('Alphabet ', source.ABC)
print('DFA: ', source.dfa)
print(source.dfa_passage(s))
print(source.tree_match(s))
print('Restore: ', source.restore())
print('----------------------------------------------------------------------------')
print('Regex inversion: ', inv.regex)
print('Alphabet: ', inv.ABC)
print('DFA inversion: ', inv.dfa)
print(inv.dfa_passage(s))
print('----------------------------------------------------------------------------')
if add:
    print('Regex addition: ', add.regex)
    print('Alphabet: ', add.ABC)
    print('DFA addition: ', add.dfa)
    print(add.dfa_passage(s))
    print('----------------------------------------------------------------------------')
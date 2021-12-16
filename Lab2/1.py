from Treebuild import *


class myre_compile(object):

    def __init__(self, regex, ABC):
        self.tree, _ = tree_builder(Parser(regex))
        self.DFA = min_DFA2(DFA_builder(NFA_builder(self.tree), ABC), ABC)

    def restore(self):
        return regex

    def inversion(self):
        pass

    def addition(self):
        pass


class myre_findall(object):

    def __init__(self, regex: str, string: str):
        self.tree = tree_builder(Parser(regex))

    def group_index(self, i: int == -1):
        return self.groups[i][1].__str__()

    def group_name(self, name: str):
        return [j.__str__() for j in [i for i in self.groups if self.groups[i][0] == name]]

    def __str__(self):
        pass


class myre(object):

    def compile(regex):
        return myre_compile(regex)

    def findall(regex, string):
        return myre_findall(regex, string)


regex = 'as{2}da?a|ds*'
regex = '(' + regex + ')'
tokens = Parser(regex)
tree = tree_builder(tokens)

print('Tree:', tree)

ABC = 'asd'

NFA = NFA_builder(tree)
print(NFA)

DFA = DFA_builder(NFA, ABC)
print(DFA)

minDFA = min_DFA2(DFA, ABC)
print(minDFA)

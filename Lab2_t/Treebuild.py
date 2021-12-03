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


symbols = set(['*', '|', '{', '}', '%', '(', ')'])

def Parser(regex):
    tokens = []
    i = 0

    while i < len(regex):
        if regex[i] not in symbols:
            tokens.append(Token('literal', regex[i]))
        elif regex[i] == '%':
            if i+2 < len(regex) and regex[i+2] == '%':
                tokens.append(Token('literal', regex[i+1]))
                i += 2
        elif regex[i] == '{':
             if i+2 < len(regex) and regex[i+2] == '}':
                tokens.append(Token('token', int(regex[i+1])))
                i += 2
        elif regex[i] == '(' or regex[i] == ')' or regex[i] == '*' or regex[i] == '|':
            tokens.append(Token('token', regex[i]))
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
        if tokens[first+1].is_literal():
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

            elif tokens[i] == '*' or type(tokens[i].value) == int:
                if parent:
                    if parent.right:
                        parent.right = BinTree(tokens[i], parent.right, None)
                else:
                    groot = BinTree(tokens[i], groot, None)

        tokens = tokens[:first] + [groot] + tokens[last+1:]
        first, last = find_pair(tokens)

    return tokens[0]

    
def tree_builder_2(tokens: list):
    first, last = find_pair(tokens)
    while first != -1:
        Nodes = []
        i = -1
        while '|' in tokens:
            t = tokens[i+1:].index('|')
            Nodes.append(tokens[i+1:t])
            i = t
        Nodes.append(tokens[i+1:])

        if len(Nodes) > 1:
            group_root = BinTree(Token('token', '|'), Nodes[0], Nodes[1])
            cur = group_root.right
            parent = group_root
            for i in range(2,len(Nodes)):
                parent.right = BinTree(Token('token', '|'), cur, Nodes[i])
                parent = parent.right
                cur = parent.right
        else:
            group_root = BinTree(Nodes[0], None, None)

    tokens = tokens[:first] + tokens[last+1:]
    first, last = find_pair(tokens)

regex = '|(s*)df'
regex = '(' + regex + ')'
tokens = Parser(regex)
res = tree_builder(tokens)
print(res)
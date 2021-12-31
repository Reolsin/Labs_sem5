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

    def is_group(self):
        return self.type == 'group_name'

    def __str__(self):
        return self.value


symbols = set(['*', '|', '{', '}', '%', '(', ')', '?', '<', '>'])


def Parser(regex: str):
    tokens, i, ng = [], 0, 0
    ABC = set()

    while i < len(regex):
        if regex[i] not in symbols:
            tokens.append(Token('literal', regex[i]))
            ABC.add(regex[i])
        elif regex[i] == '%':
            i += 1
            while i < len(regex) and regex[i] != '%':
                tokens.append(Token('literal', regex[i]))
                ABC.add(regex[i])
                i+=1
            if i == len(regex):
                raise Exception('Parsing error. Shielded group not closed.')
        elif regex[i] == '{':
            j = i + 1
            while j < len(regex) and regex[j].isdigit():
                j += 1
            if j != len(regex) and regex[j] == '}' and i != j+1:
                tokens.append(Token('token', int(regex[i+1:j])))
                i = j
            else:
                raise Exception('Parsing error. Token not recognized.')
        elif regex[i] == '(':
            tokens.append(Token('token', regex[i]))
            gname = None
            if i+1 < len(regex):
                if regex[i+1] == '<':
                    j = i+2
                    while j < len(regex)  and regex[j] != '>':
                        if not (regex[j].isalpha() or regex[j].isdigit()):
                            pass
                        j += 1
                    if j != len(regex):
                        gname = regex[i+2:j]
                    else:
                        raise Exception('Parsing error. Error in reading group <name>. String index:{}'.format(j))
            else:
                raise Exception('Parsing error. Error in reading (group). String index:{}'.format(i+1))
            tokens.append(Token('group_name', [ng, gname]))
            ng += 1
        elif regex[i] == '*' or regex[i] == '|' or regex[i] == '?' or regex[i] == ')':
            tokens.append(Token('token', regex[i]))
        else:
            raise Exception('Parsing error. Token not recognized.')
        i += 1

    return tokens, ABC

    
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
            groot = None
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

        groot = BinTree(tokens[first+1], groot, None)
        tokens = tokens[:first] + [groot] + tokens[last+1:]
        first, last = find_pair(tokens)
        if first == -1 ^ last == -1:
            pass

    return tokens[0]
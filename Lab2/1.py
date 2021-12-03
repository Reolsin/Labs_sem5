
class Token:

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return "['"+ self.token + "', " + self.type +']'

class Tree:

    def __init__(self, token: Token, kids: list):
        self.token = token
        self.kids = kids

    def add_kid(self, kid):
        self.kids.append(kid)

    def add_kids(self, kids: list):
        for kid in kids:
            self.add_kid(kid)

    def __str__(self):
        return self.token.__str__() + ': ' + '(' + ','.join([kid.__str__() for kid in self.kids]) + ')'



class myre_compile(object):

    def __init__(self, regex):
        pass

    def restore(self):
        pass

    def inversion(self):
        pass

    def addition(self):
        pass



class myre_findall(object):


    def __init__(self, regex: str, string: str):

        tokens = list(regex)

        self.groups = []
        if brackets_is_correct(regex):
            generate_groups(self.groups, regex)
        pass

    def group(self, i):
        pass

    def __str__(self):
        pass



class myre(object):

    def compile(regex):
        
        return myre_compile(regex)

    def findall(regex, string):

        return myre_findall(regex, string)



def find_bracket_group(regex, start, end):
    n = start
    count = 0
    for i in range(start + 1, end):
        if regex[i] == '(':
            if start == n:
                start = i
            count+=1
        if regex[i] == ')' and start != n:
            count-=1
            if count == 0:
                end = i
                return start, end
    
    return start, end

def brackets_is_correct(regex):
    count = 0
    for i in regex:
        if i == '(':
            count+=1
        elif i == ')':
            count-=1
        if count < 0:
            return False
    if count == 0:
        return True
    else:
        return False

def generate_groups(groups: list, regex: str):
    start, end = -1, len(regex)
    t = 0

    while end != t:
        groups.append(regex[start + 1:end])
        t = end
        start, end = find_bracket_group(regex, start, end)
        if t == end:
            start, end, t = end, len(regex), len(regex)
            start, end = find_bracket_group(regex, start, end)


def splt(string: str, s: str):
    res = []
    start = 0
    count = 0

    for i in range(len(string)):
        if string[i] == '(':
            count+=1
        elif string[i] == ')':
            count-=1
        if count == 0:
            if string[i] == s:
                end = i
                res.append(string[start:end])
                start = i + 1
    end = len(string)
    res.append(string[start:end])           
    
    return res

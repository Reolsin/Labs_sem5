from smc import Lab1_sm

def my_split(string, separate_symols: list):

    res = []
    if string:
        k = 0
        for i in range(len(string)):
            if string[i] in separate_symols:
                res.append(string[k:i])
                k = i
        res.append(string[k:])

    return res

class SMCParser():

    digits = '0123456789'
    literals = 'qwertyuiopasdfghjklzxcvbnm'

    def __init__(self):
        self._fsm = Lab1_sm.Name_checker_sm(self)

    def clear(self):
        self._fsm.setState(Lab1_sm.NameMap.Start)

    def parse(self, inp: str):
        self.clear()
        if len(inp) < 7 or len(inp) > 80 or inp[0:6] != 'irc://':
            return None
        tokens = my_split(inp[6:], ['?','/',':'])
        for token in tokens:
            if token:
                if self.check_header(token):
                    self._fsm.get_header(token)
                elif self.check_port(token):
                    self._fsm.get_port()
                elif self.check_name(token):
                    self._fsm.get_name()
                elif self.check_pass(token):
                    self._fsm.get_pass()
                else:
                    self._fsm.end()
                    break
        self._fsm.end()
        if type(self._fsm.getState()) is Lab1_sm.NameMap_OK:
            return self._server_name
        elif type(self._fsm.getState()) is Lab1_sm.NameMap_ERROR:
            return None

    def remember(self, serv):
        self._server_name = serv

    def check_header(self, t):
        for i in t:
            if i not in (self.digits + self.literals):
                return False
        return True

    def check_port(self, t):
        if t[0] == ':' and len(t) > 1:
            t = t[1:]
            if t.isdigit() and int(t) < 65536 and int(t) > 0:
                return True
        return False
        
    def check_name(self, t):
        if t[0] == '/' and len(t) > 1:
            for i in t[1:]:
                if i not in (self.digits + self.literals):
                    return False
            return True
        return False
        
    def check_pass(self, t):
        if t[0] == '?' and len(t) > 1:
            for i in t[1:]:
                if i not in (self.digits + self.literals):
                    return False
            return True
        return False
    
    def go_to_Default(self):
        pass


def Check_smc(string):

    return SMCParser().parse(string)

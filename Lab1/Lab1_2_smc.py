import Lab1_2_sm

class SMCParser():

    buffer = ''
    server = ''

    digits = '0123456789'
    literals = 'qwertyuiopasdfghjklzxcvbnm'

    def __init__(self):
        self._fsm = Lab1_2_sm.Name_checker_sm(self)

    def clear(self):
        self._fsm.setState(Lab1_2_sm.NameMap.Start)
        self.buffer = ''
        self.server = ''

    def parse(self, input_: str):
        self.clear()
        if len(input_) > 80:
            return None
        for s in input_:
            if s == '/':
                self._fsm.slash()
            elif s == ':':
                self._fsm.dots(s)
            elif s == '?':
                self._fsm.q_s(s)
            elif s in self.literals:
                self._fsm.char(s)
            elif s in self.digits:
                self._fsm.digit(s)
            else:
                self._fsm.error()
            if type(self._fsm.getState()) is Lab1_2_sm.NameMap_ERROR:
                break
        self._fsm.end()
        if type(self._fsm.getState()) is Lab1_2_sm.NameMap_ERROR:
            return None
        else:
            return self.server
        
    def add_char_serv(self, s):
        self.server += s

    def add_buffer(self, s):
        self.buffer += s

    def check_header(self):
        return self.buffer == 'irc:'

    def check_port(self):
        return int(self.buffer) <= 65535
    
    def clear_buffer(self):
        self.buffer = ''

def Check_2_smc(string):

    return SMCParser().parse(string)

print(Check_2_smc('irc://a:1/a?a'))
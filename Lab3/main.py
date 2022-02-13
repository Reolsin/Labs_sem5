from yacc import *
from test_progs import text

def run(text):
    prog = parser.parse(text + '\n')

    map_file = open('map.txt')
    try:
        prog.find_exit(map_file)
    except Exception as e:
        prog.set_exception(e)
        return prog.exception
    return 'Interpreter finished script executing. Robot didnt found exit.'

def test_run(text):
    prog = parser.parse(text + '\n')
    map_file = open('map.txt')
    prog.find_exit(map_file)
    print()

print(run(text))

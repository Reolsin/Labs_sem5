import csv
from random import randint, randrange

template = {'header': 'irc://','port': ':', 'name': '/','pass': '?',}
keys = list(template)
max_len = 80

digits = '123456789'
Ok_symbols = 'qwertyuiopasdfghjklzxcvbnm' + digits
Er_symbols = ' _%^[]{}<>#@'


str_len = 0

def gen_token(key, correct, length, i):
    global str_len
    token = list(template[key])

    str_len += len(token)
    p = max_len - (length - 1)*2 + i*2 - str_len

    if key == 'port':
        if p >= 5:
            rand = list(str(randint(1, 65535)))
            token += rand
            n = len(rand)
        else:
            n = randint(1, p)
            token += [digits[randrange(0, len(digits))] for _ in range(n)]
    else:
        n = randint(1, p)
        token += [Ok_symbols[randrange(0, len(Ok_symbols))] for _ in range(n)]
    str_len += n

    if not correct:
        for i in range(randrange(0, len(token) // 5 + 1)):
            token[randrange(0, len(token))] = Er_symbols[randrange(0, len(Er_symbols))]
    
    return ''.join(token)


def generator(number: int):
    global str_len
    res = []

    for n in range(number):
        length = randint(1, 4)
        correct = randint(0, 1)
        string = ''.join([gen_token(keys[i], correct, length, i) for i in range(len(keys)) if i < length])
        str_len = 0

        res.append([string, correct, length])

    return res



with open('output/generated_sequence.csv', 'w') as output_file:
    writer = csv.writer(output_file)
    for row in generator(1000):
        writer.writerow(row)
    output_file.close()


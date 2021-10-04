from Lab1_1 import Check_my2
from Lab1_re import Check_re
from Lab1_lex import Check_lex
from Lab1_smc import Check_smc
import csv



def use_method(s: str, string: str):

    res = None
    if s == 'my':
        res = Check_my2(string)
    elif s == 're':
        res = Check_re(string)
    elif s == 'lex':
        res = Check_lex(string)
    elif s == 'smc':
        res = Check_smc(string)

    return res

method = ['my', 're', 'lex', 'smc']

menu = ["Keyboard", "File", "Exit"]
options = list(menu)
options.sort()
while True: 
    for i in range(len(menu)): 
        print(i + 1, menu[i])

    selection = input("Choose option:\n")
    if selection == '1':
        for i in method: 
            print(i)
        s = input("Choose method:\n")
        if s in method:
            string = input("Enter string:\n")
            res = use_method(s, string)
            if res:
                print("correct")
            else:
                print("wrong")
        else:
            print("Input Error")

    elif selection == '2':
        servers = {}
        for i in method: 
            print(i)
        s = input("Choose method:\n")
        if s in method:
            filename = input("Enter filename:\n")
            file = open(filename, 'r')
            if file:
                out_filename = 'output/' + filename[:filename.index('.')] + '_out_' + s + '.csv'
                with open(out_filename, 'w') as out_file:
                    writer = csv.writer(out_file)
                    for string in [line[:-1] for line in file]:
                        res = use_method(string)
                        if res is not None:
                            if res not in servers:
                                servers[res] = 1
                            else:
                                servers[res] += 1
                            writer.writerow([string, 'correct'])
                        else:
                            writer.writerow([string, 'wrong'])
                    for name in servers:
                        writer.writerow([name, servers[name]])
                file.close()
                out_file.close()
                print("Success")
        else:
            print("Input Error")

    elif selection == '3':
        print("Exit...")
        break
    else: 
        print("Unknown Option Selected!")
import csv

def ord_is_correct(symbol):
    n = ord(symbol)
    return ((n>47 and n<58) or (n>96 and n<123))

def slice_is_correct(string, i, k):
    while i < k: #pass
        if not(ord_is_correct(string[i])):
            return 0
        i+=1
    return 1

def Check_my(string):
    max_len = 80
    i = 0
    k = 0
    n = 0

    if len(string.lower()) <= max_len and len(string) > 6:
        max_len = len(string)
    else:
        return None
    
    if string[0:6] != 'irc://': #irc://
        return None

    k = i
    while k < max_len: #check :
        if string[k] == ':':
            break
        k+=1
    else:
        return None

    if not(slice_is_correct(string, i, k)): #server
        return None
    server = string[i:k]
    i = k+1
        
    k = i
    while k < max_len and n < 6: #check /
        if string[k] == '/':
            break
        k+=1
        n+=1
    else:
        return None

    if not(int(string[i:k]) < 65535): #port
        return None
    i = k+1

    k = i
    while (k < max_len): #check ?
        if string[k] == '?':
            break
        k+=1
    else:
        return None

    if not(slice_is_correct(string, i, k)): #login
        return None
    i = k+1

    if not(slice_is_correct(string, i, max_len)): #pass
        return None

    return server

menu = {}
menu['1']="Keyboard"
menu['2']="File"
menu['3']="exit"
options = list(menu)
options.sort()
while True: 
    for entry in options: 
        print(entry, menu[entry])

    selection = input("Choose option:\n") 
    if selection =='1':
        str = input("Enter string:\n")
        if Check_my(str):
            print("correct")
        else:
            print("wrong")

    elif selection == '2':
        servers = {}
        filename = input("Enter filename:\n")
        file = open(filename, 'r')
        if file:
            out_filename = filename[:filename.index('.')] + '_out_v1.csv'
            with open(out_filename, 'w') as out_file:
                writer = csv.writer(out_file)
                for string in [line[:-1] for line in file]:
                    name = Check_my(string)
                    if name is not None:
                        name = string[6:string.find(':', 6)]
                        if name not in servers:
                            servers[name] = 1
                        else:
                            servers[name] += 1
                        writer.writerow([string, 'correct'])
                    else:
                        writer.writerow([string, 'wrong'])
                for name in servers:
                    writer.writerow([name, servers[name]])
            file.close()
            out_file.close()

    elif selection == '3':
      print("Exit...")
      break
    else: 
      print("Unknown Option Selected!")
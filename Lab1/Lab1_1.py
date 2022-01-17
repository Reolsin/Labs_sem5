
def ord_is_correct(symbol):
    n = ord(symbol)
    return ((n>47 and n<58) or (n>96 and n<123))

def is_digit(symbol):
    n = ord(symbol)
    return (n>47 and n<58)

def Check_my2(string):

    max_len = 80
    i = 6
    n = 0

    if len(string.lower()) <= max_len and len(string) > 6:
        max_len = len(string)
    else:
        return None
    
    if string[0:6] != 'irc://': #irc://
        return None

    while i < max_len and ord_is_correct(string[i]): #server
        i+=1
    server = string[6:i]
    if i == max_len:
        return server
    elif i + 1 == max_len:
        return None
    elif string[i] != ':':
        return None
    i+=1

    while i + n < max_len and is_digit(string[i+n]) and n < 6: #port
        n+=1
    if i + n == max_len:
        return server
    elif is_digit(string[i+n]):
        return None
    elif i + n + 1 == max_len:
        return None
    elif string[i+n] != '/':
        return None
    elif string[i+n] == '/':
        if int(string[i:i+n]) > 65535:
            return None
    i += n + 1

    while i < max_len and ord_is_correct(string[i]): #login
        i+=1
    if i == max_len:
        return server
    elif string[i] != '?':
        return None
    elif i + 1 == max_len:
        return None
    i += 1

    while i < max_len and ord_is_correct(string[i]): #password
        i+=1
    if i == max_len:
        return server
    else:
        return None
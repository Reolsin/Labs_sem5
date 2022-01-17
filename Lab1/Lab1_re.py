import re
import csv

def Check_re(string):

    if len(string) > 80:
        return None

    result =  re.match(r'irc://([a-z0-9]+)(:(\d{4}|\d{3}|\d{2}|\d{1}|[0-5]\d{4}|6([0-4]\d{3}|5([0-4]\d{2}|5([0-2]\d{1}|3[0-5]))))(/([a-z0-9]+)(\?([a-z0-9]+))?)?)?$', \
        string)

    if result is None:
        return None
    return result.group(1)
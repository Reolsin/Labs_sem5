from Lab1_1 import Check_my2
from Lab1_re import Check_re
from Lab1_lex import Check_lex
from Lab1_smc import Check_smc
import time
import csv


with open('2.txt', 'r') as input_file:
    output_file = open('timing.csv', 'w')
    writer = csv.writer(output_file)
    t1 = time.perf_counter_ns()
    for string in [line[:-1] for line in input_file]:
        Check_my2(string)
    t2 = time.perf_counter_ns()
    writer.writerow(['my', t2-t1])

    t1 = time.perf_counter_ns()
    for string in [line[:-1] for line in input_file]:
        Check_re(string)
    t2 = time.perf_counter_ns()
    writer.writerow(['re', t2-t1])

    t1 = time.perf_counter_ns()
    for string in [line[:-1] for line in input_file]:
        Check_lex(string)
    t2 = time.perf_counter_ns()
    writer.writerow(['lex', t2-t1])

    t1 = time.perf_counter_ns()
    for string in [line[:-1] for line in input_file]:
        Check_smc(string)
    t2 = time.perf_counter_ns()
    writer.writerow(['smc', t2-t1])
    
    input_file.close()
    output_file.close()
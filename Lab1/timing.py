from typing import Sequence
from Lab1_1 import Check_my2
from Lab1_re import Check_re
from Lab1_lex import Check_lex
from Lab1_smc import Check_smc
from Lab1_2_smc import Check_2_smc
import time
import csv


with open('output/generated_sequence.csv') as input_f:
    reader = csv.reader(input_f)
    l = list(reader)
    range_ = range(0, len(l), 2)
    pairs = ['01','02','03','04','11','12','13','14', 'all']
    sources = [[l[i] for i in range_ if l[i][1] == pair[0] and l[i][2] == pair[1]] for pair in pairs if pair != 'all']
    sources.append([l[i] for i in range_])

    output_f = open('output/timing.csv', 'w')
    writer = csv.writer(output_f)


    for i in range(len(sources)):
        t1 = time.perf_counter_ns()
        for row in sources[i]:
            Check_my2(row[0])
        t2 = time.perf_counter_ns()
        writer.writerow(['my', t2-t1, pairs[i]])

        t1 = time.perf_counter_ns()
        for row in sources[i]:
            Check_re(row[0])
        t2 = time.perf_counter_ns()
        writer.writerow(['re', t2-t1, pairs[i]])

        t1 = time.perf_counter_ns()
        for row in sources[i]:
            Check_lex(row[0])
        t2 = time.perf_counter_ns()
        writer.writerow(['lex', t2-t1, pairs[i]])

        t1 = time.perf_counter_ns()
        for row in sources[i]:
            Check_smc(row[0])
        t2 = time.perf_counter_ns()
        writer.writerow(['smc', t2-t1, pairs[i]])

        t1 = time.perf_counter_ns()
        for row in sources[i]:
            Check_2_smc(row[0])
        t2 = time.perf_counter_ns()
        writer.writerow(['smc_2', t2-t1, pairs[i]])
    
    input_f.close()
    output_f.close()
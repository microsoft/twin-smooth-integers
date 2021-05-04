# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# pte_sieve.py
#
# Sieving algorithm to find twin smooth integers using PTE solutions.

import sys, time, datetime
import ctypes
from math import log, ceil
from pathlib import Path
from primes.parse import read_primes
from sieve import sieve, c_log_sieve_64, c_log_sieve_128
from pte_solutions import solutions, Collection, check_sols

def pte_sieve(L, R, b, primes, log_primes, logB, sols, proc_num, results_file,
              status_path, use_c, resume):
    print(f'{proc_num}: Sieving from {L} to {R}...')

    # File name for logging last finished interval and prime stats.
    status_filename = status_path 
    status_filename += f'/{sols.solutions_name}_{logB}_from_{L}_to_{R}'
    status_filename += f'_status_{proc_num}.txt'

    if not resume:
        # Start on the left of the interval [L,R].
        T = L
        # Count the number of x values that produce twin smooth integers.
        num_x = 0
        # Count the number of x values that make p=2*f(x)-1 prime. 
        num_primes = 0
    else:
        # Read stats and where to resume from status file.
        with open(status_filename, 'r') as status_file:
            s = status_file.readline()
            s = s.strip()
            params = [int(i) for i in s.split(',')]
            T = params[5]
            num_x = params[6]
            num_primes = params[7] 

    # Extend the range by the maximum range occurring in the solutions 
    # to overlap the intervals.
    b_ext = b + sols.max_range
   
    if use_c == 64 or use_c == 128:
        # Prepare prime data and result byte array to pass to C.
        np = len(primes)
        numbers = bytearray(b_ext)
        numbers = memoryview(numbers)
        c_primes = (ctypes.c_int * np)(*primes)
        c_log_primes = (ctypes.c_char * np)(*log_primes)
        c_positions = (ctypes.c_char * b_ext)(*numbers)

    # Count the number of sieve steps.
    sieve_count = 0

    while T < R:
        start_interval_time = time.time()
        sieve_count += 1

        if R-T < b:
            # At the end of the range, the interval might be shorter.
            # Extend the range by the maximum range occurring in the solutions
            # to overlap the intervals.
            b_ext = R - T + sols.max_range
        
        #################################################
        if use_c == 64:
            # Call the C sieve using 64-bit data types.
            c_log_sieve_64(T, b, logB, np, ctypes.byref(c_primes), 
                        ctypes.byref(c_log_primes), ctypes.byref(c_positions))
            positions = bytearray(c_positions)
        
        elif use_c == 128:
            # Call the C sieve using 128-bit data types.
            c_log_sieve_128(T, b, logB, np, ctypes.byref(c_primes), 
                        ctypes.byref(c_log_primes), ctypes.byref(c_positions))
            positions = bytearray(c_positions)

        else:
            # Call the python sieve. 
            positions = sieve(T, b_ext, logB, primes)

        #################################################
        after_sieving_time = time.time()

        # Run through the bitstring
        for j in range(b):
            # Start at the next smooth number
            if positions[j]:
                # Check whether any of the solution root patterns occur 
                # at this position in the string.
                results = check_sols(T,j,positions,sols)
                
                if not results == []:
                    print(f'\n{proc_num} ', end='')
                    for found in results:
                        num_x += 1
                        print(found)
                        if found.isprime:
                            num_primes += 1
                        # Write to file
                        with open(results_file, 'a', newline='') as sols_file:
                            sols_file.write(f'{proc_num}, {found}\n')
        
        with open(status_filename, 'w', newline='') as status_file:
            status_file.write(f'{proc_num}, {logB}, {L}, {R}, {T}, {T+b},'
                              + f' {num_x}, {num_primes}\n\n')
            status_file.write(f'Status file for process {proc_num} searching'
                              + f' for twin 2^{logB}-smooth numbers in the'
                              + f' range from {L} to {R}\n')
            status_file.write(f'Last finished sieve interval: [{T}, {T+b}],'
                              + f' {(T+b-L)/(R-L)*100} % done.\n')
            status_file.write(f'Number of x values that produce twin smooth'
                              + f' integers in [{L}, {T+b}]: {num_x}\n')
            status_file.write(f'Number of x values that produce prime 2*f(x)-1'
                              + f' in [{L}, {T+b}]: {num_primes}\n')
        
        end_interval_time = time.time()
        print(f'\n{proc_num}: Interval [{T}, {T+b-1}], {(T+b-L)/(R-L)*100} %, '
              + f'time: {round(end_interval_time - start_interval_time, 3)}s,'
              + f' spent on sieving:'
              + f' {round(after_sieving_time - start_interval_time, 3)}')
        sys.stdout.flush()
        
        T += b
    
    with open(status_filename, 'a', newline='') as status_file:
        status_file.write(f'Done!\n')


def main(args):
    import multiprocessing as mp
    # import cProfile, pstats, io

    # Left bound of the interval to be sieved (included).
    L = args[1]
    # Right bound of the interval to be sieved (excluded).
    R = args[2]
    if not L < R:
        raise RuntimeError('Left bound L must be less than right bound R.')
    
    # Length of the batches to be sieved at one time.
    b = args[3]

    # Log of the smoothness bound, currently only allowing powers of 2.
    logB = args[4]
    
    # Read a precomputed table of all primes less than B=2**logB.
    primes, log_primes = read_primes(logB)

    # Number of processes among which to divide up the full interval.
    num_proc = args[5]
    # Interval size (rounded up), the last process gets the rest.
    interval = ceil((R-L)/num_proc)
    # Left and right bounds for the subintervals.
    Li = [L + i*interval for i in range(num_proc)]
    Ri = [Li[i] for i in range(1, num_proc)] + [R]

    # Relax to allow non-smooth factors.
    relax = args[7]

    # Get the solutions.
    solutions_name = args[6]
    soldata = solutions[solutions_name]
    # Parse the solutions.
    sols = Collection(soldata, solutions_name, relax)

    # Choose which implementation to use for the sieve.
    use_c = args[8]

    # Resume or start from scratch.
    resume = args[9]

    # Create folders if they don't exist already.
    results_path = f'results_{solutions_name}_{logB}'
    Path(results_path).mkdir(parents=True, exist_ok=True)
    status_path = f'status_{solutions_name}_{logB}'
    Path(status_path).mkdir(parents=True, exist_ok=True)
    # File name to store value x and solutions that generate found 
    # twin smooth numbers.
    results_file = results_path + f'/{solutions_name}_{logB}_{L}_to_{R}.txt'
    print('Printing results to file ' + results_file)

    with open(results_file, 'a', newline='') as sols_file:
        sols_file.write(f'x values, solutions and p values of 2^{logB}-smooth'
                        + f' twin numbers for x in the range from {L} to {R}'
                        + f' - {datetime.datetime.now()}\n')

    # #profiling
    # pr = cProfile.Profile()
    # pr.enable()
    
    start_time = time.time()
    # Set up and start the parallel processes.
    processes = []
    for i in range(num_proc):
        p = mp.Process(target=pte_sieve, args=(Li[i], Ri[i], b, primes, 
                       log_primes, logB, sols, i, results_file, 
                       status_path, use_c, resume))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    print(f'Time: {round(end_time - start_time, 3)}s')

    # pr.disable()
    # s = io.StringIO()
    # sortby = 'cumulative'
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())
 

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("L", type=int, 
                        help="left bound L of the sieving interval")
    parser.add_argument("R", type=int, 
                        help="right bound R of the sieving interval")
    parser.add_argument("b", type=int, 
                        help="size b of subintervals sieved in one iteration")
    parser.add_argument("logB", type=int, 
                        help="logarithm of the smoothness bound B")
    parser.add_argument("-p", "--processes", type=int, default=1, 
                        help="number of processes to be started in parallel")
    parser.add_argument("-s", "--solutions", type=str, default="size-6", 
                        help="name of the solution list")
    parser.add_argument("-r", "--resume", default=False, 
                        help="resume from status files", action="store_true")
    parser.add_argument("-x", "--relax", type=int, default=0, 
                        help="relax to allow non-smooth factors")
    parser.add_argument("-c", "--use_c", type=int, default=0, 
                        help="use the 64- or 128-bit C code (USE_C = 64/128)")
    args = parser.parse_args()

    filename = sys.argv[0]
    
    main([filename, args.L, args.R, args.b, args.logB, args.processes, 
          args.solutions, args.relax, args.use_c, args.resume==True])
    
# The PTE sieve

The PTE sieve is a sieving algorithm to find twin smooth integers of a certain size with a desired smoothness bound. The algorithm uses a variant of the classical sieve of Eratosthenes that identifies smooth integers instead of primes. It is run on a search space of smaller integers. The output of the sieving step is then searched for specific patterns of smooth integers that correspond to solutions of the Prouhet-Tarry-Escott (PTE) problem. These solutions can be used to boost the pattern of smooth integers found among smaller numbers to twin smooth integers of the desired size.

A detailed description of the method, the algorithm and results of a range of experiments are given in

[[CMN20]](https://eprint.iacr.org/2020/1283) *Sieving for twin smooth integers with solutions to the Prouhet-Tarry-Escott problem* by Craig Costello, Michael Meyer and Michael Naehrig.

The algorithm was implemented in Python 3 and has the option of running the main sieving procedure  in C.

## Contents

The PTE sieve code contains

* [Python 3 code](sieve.py) to identify smooth integers in an interval,
* [C code](c/test_sieve.c) for the same purpose that can be used on Linux and is called from python,
* [Python 3 code](pte_sieve.py) for the PTE sieve that searches for twin smooth integers using PTE solutions,
* a list of all [primes](primes) up to 2^25, along with [Magma](http://magma.maths.usyd.edu.au/magma/) code to generate more primes,
* a collection of [solutions](pte_solutions/solution_data.py) to the Prouhet-Tarry-Escott problem that can be used with the PTE sieve,
* [results](results) from our searches including those reported in [[CMN20]](https://eprint.iacr.org/2020/1283) and a [Sage](https://www.sagemath.org/) script to analyse and check them.

## Identifying smooth integers

The code in [sieve.py](sieve.py) can be used by itself to identify smooth integers in an interval. Calling the Python help option

```console
python3 sieve.py -h
```

displays the usage of the main function:

```console
usage: sieve.py [-h] [-c USE_C] T b logB

positional arguments:
  T                     start of the sieving interval
  b                     length b of the sieving interval
  logB                  logarithm of the smoothness bound B

optional arguments:
  -h, --help            show this help message and exit
  -c USE_C, --use_c USE_C
                        use the 64- or 128-bit C code (USE_C = 64/128)
```

For example, in order to sieve an interval of length b = 2^18 = 262144 starting at the value T = 3141592653589793 with a smoothness bound of B = 2^23, one calls:

```console
python3 sieve.py 3141592653589793 262144 23
```

The output shows the start of a byte array that only contains 0x00 or 0x01 values. An entry 0x01 in byte i indicates that the integer T+i is B-smooth, an entry 0x00 means it is not. The code runs an exact sieve that multiplies primes to accumulator values as well as an approximate one using rounded logarithms and additions instead. The results are compared.

The -c option enables the C implementation of the logarithm based sieving, either using 64-bit or 128-bit data types. To compile both versions on Linux, run `make all` in the [c subfolder](c). After that, the following command will also run the 64-bit C implementation of the sieve and compare its results to the python version:

```console
python3 sieve.py -c 64 3141592653589793 262144 23
```

## Sieving with PTE solutions

The file [pte_sieve.py](pte_sieve.py) contains the full sieve procedure that uses solutions to the PTE problem and calls the sieving functions in [sieve.py](sieve.py) for identifying smooth integers. Typing

```console
python3 pte_sieve.py -h
```

shows how to use the PTE sieve:

```console
usage: pte_sieve.py [-h] [-p PROCESSES] [-s SOLUTIONS] [-r] [-x RELAX] [-c USE_C] L R b logB

positional arguments:
  L                     left bound L of the sieving interval
  R                     right bound R of the sieving interval
  b                     size b of subintervals sieved in one iteration
  logB                  logarithm of the smoothness bound B

optional arguments:
  -h, --help            show this help message and exit
  -p PROCESSES, --processes PROCESSES
                        number of processes to be started in parallel
  -s SOLUTIONS, --solutions SOLUTIONS
                        name of the solution list
  -r, --resume          resume from status files
  -x RELAX, --relax RELAX
                        relax to allow non-smooth factors
  -c USE_C, --use_c USE_C
                        use the 64- or 128-bit C code (USE_C = 64/128)
```

The positional arguments L and R describe the interval [L, R) to be covered by the search for smooth integers, where the right end R is not included. This interval is treated in smaller intervals of length b. Again, the smoothness bound is B = 2^logB. The optional arguments can be used to specify a number of parallel processes (via the -p option), to specify a specific set of solutions (via -s), to resume a previous run of the same L, R, b, logB values (-r), or to relax the smoothness condition to allow a non-smooth factor in the resulting twin smooth integers. The option -c allows to use the log-based sieving code in C.

As an example, the call

```console
python3 pte_sieve.py -p 4 -c 64 -s size-4 3141592653589793 3141592666696993 4194304 20
```

runs the PTE sieve on the interval [3141592653589793, 3141592666696993), which is divided into 4 sub-intervals that are processed in parallel. The code uses the 64-bit C implementation for the sieve and checks against the set of PTE solutions of size 4 that are labeled *size-4*, processes each range in sub-intervals of size 4194304 and identifies 2^20-smooth integers.

## Results

The subfolder [results](results) contains lists of twin smooth integers that were found searching large intervals and using various sets of PTE solutions as described in [[CMN20]](https://eprint.iacr.org/2020/1283). Using [Sage](https://www.sagemath.org/), the result files can be analyzed and filtered using the script [read_results.sage](results/read_results.sage).

## Contributors

* Craig Costello
* Patrick Longa
* Michael Meyer
* Michael Naehrig

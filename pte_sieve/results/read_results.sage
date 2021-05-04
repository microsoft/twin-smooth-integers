# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# read_results.sage
#
# Sage code to read and analyze results from the pte_sieve.

def read_results(filename, bitsizes, maxB, minMN):
    with open(filename, 'r', newline='') as results_file:
        s = results_file.readline()
        s = s.strip()
        print(s)

        ints = 0
        primes = {}

        line = results_file.readline()
        while line:
            ints += 1
            line = line.strip()
            isprime = line[-5:].strip() == 'True'
            if isprime:
                linelist = line.split(', ')
                x = Integer(linelist[1][2:])
                p = Integer(linelist[len(linelist)-2][2:])
                primes[x] = p
                fact_plus = factor(p+1)
                fact_minus = factor(p-1)
                M = 1
                iM = 0
                while M.nbits() < minMN and iM < len(fact_plus):
                    iM +=1
                    Mfact = Factorization(fact_plus[:iM])
                    M = Mfact.value()
                
                N = 1
                iN = 0
                while N.nbits() < minMN and iN < len(fact_minus):
                    iN +=1
                    Nfact = Factorization(fact_minus[:iN])
                    N = Nfact.value()

                lM = (Mfact[len(Mfact)-1][0]).nbits()
                lN = (Nfact[len(Nfact)-1][0]).nbits()

                if p.nbits() in bitsizes and lM <= maxB and lN <= maxB:
                    print(f'\n{line}')
                    print(f'sage is_prime? {p.is_prime(proof=True)}')
                    print(f'p+1 = {fact_plus}')
                    print(f'p-1 = {fact_minus}')
                    print(f'log(p) = {p.nbits()}, largest prime factors: '
                        + f'{(fact_plus[len(fact_plus)-1][0]).nbits()}, ' 
                        + f'{(fact_minus[len(fact_minus)-1][0]).nbits()} bits')
                    print(f'log(M) = {M.nbits()}, largest prime factor:'
                        + f' {lM} bits')
                    print(f'log(N) = {N.nbits()}, largest prime factor:'
                        + f' {lN} bits')

            line = results_file.readline()

        print(f'\nFound integers: {ints}, primes: {len(primes)} ' 
                + f'({round(100*len(primes)/ints,2)}%)')


read_results('size-6_16_1099511627776_to_2199023255552.txt', 
                    range(240,259), 16, 210)
read_results('size-6_16_2199023255552_to_4398046511104.txt', 
                    range(240,259), 16, 210)
read_results('size-6_16_4398046511104_to_8796093022208.txt', 
                    range(240,259), 16, 210)
read_results('size-6_16_8796093022208_to_17592186044416.txt', 
                    range(240,259), 16, 210)
read_results('size-6_16_17592186044416_to_35184372088832.txt', 
                    range(240,259), 16, 210)
read_results('size-6-squ_22_73786888333907984384_to_73786941110466117632.txt', 
                    range(370,386), 22, 320)
read_results('size-6-squ_22_73786941110466117632_to_73786976294838206464.txt', 
                    range(370,386), 22, 320)
read_results('size-6-squ_23_73786976294838206464_to_73788102194745049088.txt', 
                    range(370,386), 22, 320)
read_results('size-6-squ_22_74939897799445053440_to_74940038536933408768.txt', 
                    range(370,386), 22, 320)
read_results('size-6-squ_22_110680464442257309696_to_110680569995373576192.txt', 
                    range(370,386), 22, 320)
read_results('size-12_28_508213394906208_to_526350390753968.txt', 
                    range(510,514), 28, 460)
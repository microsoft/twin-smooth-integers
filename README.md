# Twin smooth integers

This repository provides code to find *twin smooth integers*, which are two consecutive integers m and m+1 that both only have small prime factors.

More precisely, an integer is *B-smooth* for some positive number B if all of its prime divisors are less than or equal to B. The number B is called the smoothness bound. *Twin B-smooth integers* are simply two consecutive numbers that are both B-smooth. A possible application of such pairs of numbers is that they can be used as parameters for some isogeny-based cryptosystems.

## The PTE sieve

The PTE sieve is a sieving algorithm to find twin smooth integers of a certain size with a desired smoothness bound. The algorithm uses a variant of the classical sieve of Eratosthenes that identifies smooth integers instead of primes. It is run on a search space of smaller integers. The output of the sieving step is then searched for specific patterns of smooth integers that correspond to solutions of the Prouhet-Tarry-Escott (PTE) problem. These solutions can be used to boost the pattern of smooth integers found among smaller numbers to twin smooth integers of the desired size.

A detailed description of the method, the algorithm and results of a range of experiments are given in the paper
[Sieving for twin smooth integers with solutions to the Prouhet-Tarry-Escott problem](https://eprint.iacr.org/2020/1283).

The algorithm was implemented in Python 3 and has the option of running the main sieving procedure in C. See [pte_sieve/README](pte_sieve/README.md) for more details and instructions on how to use the code.

### Contributors

* Craig Costello
* Patrick Longa
* Michael Meyer
* Michael Naehrig

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

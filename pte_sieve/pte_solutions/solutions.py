# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# solutions.py
# 
# Classes to handle solutions and collections of solution.

from math import prod
from collections import Counter
from .primality import is_prime

# Import the solution data.
from .solution_data import solutions

class Solution:
    '''Class to represent a PTE solution and its associated data.'''
    def __init__(self, solution, relax):
        # The solution, given as a tuple of two lists, 
        # each containing the roots of f or g.
        self.solution = solution
        # Roots of the first polynomial.
        self.ui = self.solution[0]
        # Roots of the second polynomial.
        self.vi = self.solution[1]
        # Is the solution symmetric?
        self.symmetric = self.solution[2]
        # The degree of polynomials f and g, equals the size of the solution.
        self.degree = len(self.ui)
        assert(len(self.vi)==self.degree)

        # Make a single sorted list with all roots of both polynomials.
        self.allroots = sorted(self.ui + self.vi)
        # Normalize to have minimal root = 0.
        self.shift = self.allroots[0]
        self.allroots = [root - self.shift for root in self.allroots]
        self.ui = [root - self.shift for root in self.ui]
        self.vi = [root - self.shift for root in self.vi]

        # Compute the constant terms of each polynomial.
        self.f0 = ((-1)**self.degree)*(prod(self.ui))
        self.g0 = ((-1)**self.degree)*(prod(self.vi))
        # Order them such that f has the larger constant term.
        if self.f0 < self.g0:
            self.ui, self.vi = self.vi, self.ui
            self.f0, self.g0 = self.g0, self.f0
        # Compute the difference constant c.
        self.c = self.f0 - self.g0
        # The bit length of c.
        self.len_c = self.c.bit_length()

        # Remove duplicates in the list of roots.
        self.setroots = list(dict.fromkeys(self.allroots))
        self.setui = list(dict.fromkeys(self.ui))
        self.setvi = list(dict.fromkeys(self.vi))
        # Keep the maximal root for each solution.
        self.maxroot = self.setroots[len(self.setroots)-1]
        # Keep the solution range.
        self.range = self.maxroot        
        
        # Roots ri are ordered in increasing order, i.e. terms x-ri are 
        # decreasing. To make that pattern the right order, take the -ri in
        # increasing order and shift them to start at 0. This is the same as 
        # setroots for symmetric solutions if minroot is 0.
        self.setroots_flip = sorted([-root + self.maxroot 
                                    for root in self.setroots])

        if relax==1:
            # Relax 1 of the linear terms in either f or g to be allowed to
            # have larger factors, i.e. to be non-smooth.
            self.relaxed_setroots = {}
            self.relaxed_setroots_flip = {}
            # Count multiplicities of roots.
            ctr_ui = Counter(self.ui)
            ctr_vi = Counter(self.vi)
            # Collect only single roots.
            self.single_ui = [root for root in ctr_ui if ctr_ui[root] == 1]
            self.single_vi = [root for root in ctr_vi if ctr_vi[root] == 1]
            if len(self.single_ui) == 0:
                self.single_roots = [[v] for v in self.single_vi]
            elif len(self.single_vi) == 0:
                self.single_roots = [[u] for u in self.single_ui]
            else:
                self.single_roots = [[u,v] for u in self.single_ui 
                                           for v in self.single_vi] 
            # Produce rootsets with at most one single root removed from 
            # each of the ui or vi.
            for root in self.single_roots:
                key = f'{root[0]}'
                for r in root[1:]:
                    key += f', {r}'
                self.relaxed_setroots[key] = sorted([r for r in self.setroots 
                                                     if not r in root])
                relaxed_maxroot = (self.relaxed_setroots[key]
                                        [len(self.relaxed_setroots[key]) - 1])
                self.relaxed_setroots_flip[key] = sorted([-r + relaxed_maxroot 
                                        for r in self.relaxed_setroots[key]])

    def f_eval(self, x):
        '''Evaluate the polynomial f(x) = prod(x-ui).'''
        return prod([(x-ui) for ui in self.ui])

    def g_eval(self, x):
        '''Evaluate the polynomial g(x) = prod(x-vi) = f(x) - c.'''
        return self.f_eval(x) - self.c
    
    def f_div_c(self, x):
        '''Compute f div c.'''
        f = self.f_eval(x)
        return f//self.c

    def is_int_f_div_c(self, x):
        '''Check whether f(x) is divisible by c.'''
        f = self.f_eval(x)
        return (f % self.c == 0)


def check_pattern(j, positions, roots):
    '''Check whether the pattern given by roots occurs at position j.'''
    for root in roots:
        if not positions[j+root]:
            return False
    
    return True


def check_sols(T, j, positions, sols):
    '''Collect solutions with matching bit strings at position j.'''
    xL = T + j
    results = []

    results = sols.traverse('0', xL, j, positions, results)

    return results


class Node: 
    '''Class to describe a rudimentary version of a node in a tree. 
    The only feature we need is that the node has the concept of 
    children and knows when it is a leaf and in that case has some 
    additional data to store the leaf solution.
    '''
    def __init__(self, name, level, number, children=None, leaf_solution=None):
        self.name = name
        self.level = level
        self.number = number
        self.children = children
        self.leaf_solution = leaf_solution
    
    def is_leaf(self):
        return self.children==None
    
    def __repr__(self):
        return (f"Node('{self.name}: children: {self.children}, "
                + f"sol: {self.leaf_solution})")


class Found:
    '''Class to collect information for a found x that gives twin 
    smooth integers.
    '''
    def __init__(self, x, solution):
            self.x = x
            self.solution = solution
            self.p = 2*solution.f_div_c(x) - 1
            self.isprime = is_prime(self.p)

    def __repr__(self):
        return (f'x={self.x}, solution: {self.solution.ui}, {self.solution.vi},'
               + f' p={self.p}, p prime? {self.isprime}')

    def makelist(self):
        '''Return a list of the information of a found x.'''
        return ([self.x] + self.solution.ui + self.solution.vi 
                        + [self.p, self.isprime])


class Collection:
    '''Class to organize a family of solutions and collect data 
    associated with the whole family.
    '''
    def __init__(self, solutions, solutions_name, relax):
        # Make a dictionary of parsed solutions and attach some 
        # additional information.

        # Name of the solution list.
        self.solutions_name = solutions_name

        # The number of solutions.
        self.num_sols = len(solutions)
        
        # Create a dictionary for holding the parsed solutions.
        self.solutions = {}
        if relax==1:
            self.relaxed_solutions = {}

        # Parse the solutions.
        for i in range(self.num_sols):
            self.solutions[i] = Solution(solutions[i], relax)
        
        # Get the maximum range of the roots over all solutions 
        # in this collection.
        self.max_range = max([sol.range for sol in self.solutions.values()])
        
        # Collect the sets of roots to be used for constructing the tree.
        self.rootsets = self.tree_rootsets(relax)
        
        # Generate the tree given by the hitting sets for solution checking.
        self.tree = {}
        self.next_level('0',0,0,0,self.rootsets)
    
    def tree_rootsets(self, relax):
        '''Takes all root sets constructed from the chosen solutions.'''
        rootsets = {}
        for key in self.solutions:
            if relax==1:
                # Predetermined hitting set
                hitset = [1,2,5]
                for root in self.solutions[key].relaxed_setroots:
                    # Only use the root set if it has a common element 
                    # with a given hitting set.
                    if ([r for r in 
                        self.solutions[key].relaxed_setroots_flip[root][1:] 
                        if r in hitset] != []):
                        # Flip solutions to allow checks of values x+ri to
                        # avoid overlapping on the left of the interval.
                        rootsets[key, 'plus', root] = (self.solutions[key]
                                         .relaxed_setroots_flip[root][1:])
                    if not self.solutions[key].symmetric:
                        # Only use the root set if it has a common element with
                        # a given hitting set.
                        if ([r for r in 
                            self.solutions[key].relaxed_setroots[root][1:]
                            if r in hitset] != []):
                            # For non-symmetric solutions, negative x values
                            # lead to different polynomials, include those too.
                            rootsets[key, 'minus', root] = (self.solutions[key]
                                                   .relaxed_setroots[root][1:])
            else:
                # Flip solutions to allow checks of values x+ri to avoid 
                # overlapping on the left of the interval.
                rootsets[key, 'plus'] = self.solutions[key].setroots_flip[1:]
                if not self.solutions[key].symmetric:
                    # For non-symmetric solutions, negative x values lead to 
                    # different polynomials, include those as well.
                    rootsets[key, 'minus'] = self.solutions[key].setroots[1:]

        return rootsets

    
    def max_occurrence(self, rootset_dict):
        '''Returns the most common element in a dictionary of root
        sets and its frequency.
        '''
        roots_power_set = []
        for s in rootset_dict.values():
            roots_power_set += s
        c = Counter(roots_power_set)

        return c.most_common(1)[0]

   
    def next_level(self, name, level, number, frequency, rootset_dict):
        '''Function to recursively construct the solution tree.'''
        
        # Generate a node in the tree
        self.tree[name] = Node(name, level, number)

        if frequency == 1:
            # This node is a leaf.
            # All remaining solutions in the set need to be checked.
            self.tree[name].leaf_solution = rootset_dict
        else:
            # This node has children.
            self.tree[name].children = []
            # Collect frequencies of the most frequent numbers.
            freqs = {}
            # Collect the root sets for the next level of the tree.
            new_rootset_dicts = {}

            # Work through all solutions in the set.
            while not rootset_dict == {}:
                # Get the most frequent element in the root sets.
                (num, freq) = self.max_occurrence(rootset_dict)
                # Include the most frequent number in the hitting set.
                self.tree[name].children.append(num)
                # Keep its frequency.
                freqs[num] = freq
                # Start a dictionary for the solution set for all those that
                # include num.
                new_rootset_dicts[num] = {}
                # Remove those from the starting set and include them in the 
                # set for the number num for the next iteration, but with num 
                # removed.
                remove_list = [ind for ind in rootset_dict 
                               if num in rootset_dict[ind]]
                for ind in remove_list:
                    s = rootset_dict.pop(ind)
                    s.remove(num)
                    new_rootset_dicts[num][ind] = s

            # Iterate over all children of the node and recurse.
            for num in self.tree[name].children:
                new_name = name + f'->{num}'
                self.next_level(new_name, level+1, num, freqs[num], 
                                new_rootset_dicts[num])
                        
                        
    def traverse(self, name, xL, J, positions, results):
        '''Traverse the solution tree for pattern checking.'''
        node = self.tree[name]
        if node.is_leaf():
            # Check solutions in leave node.
            soldict = node.leaf_solution
            for key in soldict:
                sol = soldict[key]
                # Check the solution pattern against the smoothness bit string.
                found = check_pattern(J, positions, sol)
                if found:
                    num_sol = key[0]
                    solution = self.solutions[num_sol]
                    if key[1] == 'plus':
                        # This case uses (x+ri) in the checks, standard for 
                        # symmetric solutions. To account for the flipped set 
                        # of roots, the x value needs to be taken at the end 
                        # of the root set.
                        x = xL + solution.maxroot
                    else:
                        # This case uses (x-ri) in the checks and is added for
                        # non-symmetric solutions. It corresponds to taking 
                        # negative x.
                        x = -xL
                    # Correct for a possible shift if the minimal root was 
                    # not 0.
                    x += solution.shift
                    # Does the polynomial f evaluate to an integer?
                    is_int = solution.is_int_f_div_c(x)
                    if is_int:
                        results.append(Found(x, solution))
        else:
            # If the node is not a leaf, go through all its children and 
            # recurse.
            for num in node.children:
                if positions[J+num]:
                    new_name = name + f'->{num}'
                    results = self.traverse(new_name, xL, J, positions, 
                                            results)
        
        return results
    





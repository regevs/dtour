#
# Useful utilities
# 
__author__ = "Regev Schweiger"


import sys
import itertools


#
# public decorator
#
# Recipe 576993 (r1): "public" decorator, adds an item to __all__ 
import sys

def public(f):
    """"Use a decorator to avoid retyping function/class names.

    * Based on an idea by Duncan Booth:
    http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
    * Improved via a suggestion by Dave Angel:
    http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1
    """
    all = sys.modules[f.__module__].__dict__.setdefault('__all__', [])
    if f.__name__ not in all:  # Prevent duplicates if run from an IDE.
        all.append(f.__name__)
    return f

def out(lst, max_width=100, index=False, spaces=3, ret=False):
    """
    Prints nicely. If this is a list of lists, some alignment is attempted.

    lst -
        The list to print

    index -
        If this is a list, whether to mark line numbers.

    max_width -
        Maximum width for a field in an alignment.

    spaces -
        Number of spaces between fields

    ret -
        Return the string or print it
    """
    # Not even a list - just print
    if not isinstance(lst, (list,tuple)):
        print lst
        return

    # List of lists of same size
    strs = []
    if all([isinstance(l, (list,tuple)) for l in lst]) and all([len(l) == len(lst[0]) for l in lst]):
            L = len(lst[0])
            temp_strs = []
            for l in lst:
                temp_line = []
                for x in l:
                    temp_line.append(str(x))
                temp_strs.append(temp_line)
            fields_sizes = []
            for i in range(L):
                temp_size = []
                for ts in temp_strs:
                    temp_size.append(len(ts[i]))
                fields_sizes.append(temp_size)
            widths = [min(max(fs),max_width) for fs in fields_sizes]
            for i,l in enumerate(lst):
                temp = ''
                for j,x in enumerate(l):
                    temp += temp_strs[i][j].ljust(widths[j])+' '*spaces
                strs.append(temp)

    else:
        for l in lst:
            strs.append(str(l))

    if index:
        index_width=len(str(len(strs)))
        for i in range(len(strs)):
            strs[i] = str(i).rjust(index_width)+':'+' '*spaces + strs[i]

    s = '\n'.join(strs)

    if (ret == False):
        print s
    else:
        return s

def outdict(d, sort_keys=False):
    if sort_keys:
        out(sorted(d.items(), key=lambda x: x[0]))
    else:
        out(sorted(d.items(), key=lambda x: x[1]))

#
# Simple count
#
def count(lst):
    d = {}
    for l in lst:
        d[l] = d.get(l,0)+1
    return d

def outcount(lst, sort_by_value=False):
    out(sorted(count(lst).items(), key=lambda x: x[(1 if sort_by_value else 0)]))

#
# Generators
#
def pairs(lst):
    for i in range(len(lst)):
        for j in range(i+1,len(lst)):
            yield (lst[i], lst[j])


def iterlen(iterator):
    c = 0
    for x in iterator:
        c += 1
    return c

from itertools import islice
def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return islice(iterable, n, None).next()
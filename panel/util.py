"""
Various general utilities used in the panel codebase.
"""
import re
import inspect
import numbers
import datetime as dt

from datetime import datetime
from collections import defaultdict, OrderedDict
from collections.abc import MutableSequence, MutableMapping

import param
import numpy as np

datetime_types = (np.datetime64, dt.datetime, dt.date)

from .decorator import public

__all__ = ["public"]

@public
def hashable(x):
    if isinstance(x, MutableSequence):
        return tuple(x)
    elif isinstance(x, MutableMapping):
        return tuple([(k,v) for k,v in x.items()])
    else:
        return x


@public
def isIn(obj, objs):
    """
    Checks if the object is in the list of objects safely.
    """
    for o in objs:
        if o is obj:
            return True
        try:
            if o == obj:
                return True
        except:
            pass
    return False


@public
def indexOf(obj, objs):
    """
    Returns the index of an object in a list of objects. Unlike the
    list.index method this function only checks for identity not
    equality.
    """
    for i, o in enumerate(objs):
        if o is obj:
            return i
        try:
            if o == obj:
                return i
        except:
            pass
    raise ValueError('%s not in list' % obj)


@public
def param_name(name):
    """
    Removes the integer id from a Parameterized class name.
    """
    match = re.match(r'(.)+(\d){5}', name)
    return name[:-5] if match else name


@public
def abbreviated_repr(value, max_length=25, natural_breaks=(',', ' ')):
    """
    Returns an abbreviated repr for the supplied object. Attempts to
    find a natural break point while adhering to the maximum length.
    """
    vrepr = repr(value)
    if len(vrepr) > max_length:
        # Attempt to find natural cutoff point
        abbrev = vrepr[max_length//2:]
        natural_break = None
        for brk in natural_breaks:
            if brk in abbrev:
                natural_break = abbrev.index(brk) + max_length//2
                break
        if natural_break and natural_break < max_length:
            max_length = natural_break + 1

        end_char = ''
        if isinstance(value, list):
            end_char = ']'
        elif isinstance(value, OrderedDict):
            end_char = '])'
        elif isinstance(value, (dict, set)):
            end_char = '}'
        return vrepr[:max_length+1] + '...' + end_char
    return vrepr


@public
def param_reprs(parameterized, skip=None):
    """
    Returns a list of reprs for parameters on the parameterized object.
    Skips default and empty values.
    """
    cls = type(parameterized).__name__
    param_reprs = []
    for p, v in sorted(parameterized.get_param_values()):
        if v is parameterized.param[p].default: continue
        elif v is None: continue
        elif isinstance(v, str) and v == '': continue
        elif isinstance(v, list) and v == []: continue
        elif isinstance(v, dict) and v == {}: continue
        elif (skip and p in skip) or (p == 'name' and v.startswith(cls)): continue
        param_reprs.append('%s=%s' % (p, abbreviated_repr(v)))
    return param_reprs


@public
def full_groupby(l, key=lambda x: x):
    """
    Groupby implementation which does not require a prior sort
    """
    d = defaultdict(list)
    for item in l:
        d[key(item)].append(item)
    return d.items()


@public
def get_method_owner(meth):
    """
    Returns the instance owning the supplied instancemethod or
    the class owning the supplied classmethod.
    """
    if inspect.ismethod(meth):
        return meth.__self__


@public
def is_parameterized(obj):
    """
    Whether an object is a Parameterized class or instance.
    """
    return (isinstance(obj, param.Parameterized) or
            (isinstance(obj, type) and issubclass(obj, param.Parameterized)))


@public
def isdatetime(value):
    """
    Whether the array or scalar is recognized datetime type.
    """
    if isinstance(value, np.ndarray):
        return (value.dtype.kind == "M" or
                (value.dtype.kind == "O" and len(value) and
                 isinstance(value[0], datetime_types)))
    elif isinstance(value, list):
        return all(isinstance(d, datetime_types) for d in value)
    else:
        return isinstance(value, datetime_types)


@public
def value_as_datetime(value):
    """
    Retrieve the value tuple as a tuple of datetime objects.
    """
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000)
    return value


@public
def value_as_date(value):
    if isinstance(value, numbers.Number):
        value = datetime.utcfromtimestamp(value / 1000).date()
    elif isinstance(value, datetime):
        value = value.date()
    return value

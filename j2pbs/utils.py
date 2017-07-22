import subprocess

def job2script():
    pass

def graph2script():
    pass

def graph2scripts():
    pass

def submit():
    pass

def upper_dict_key(d):
    res = {}
    for key in d:
        res[key.upper()] = d[key]
    return res

def lower_dict_key(d):
    res = {}
    for key in d:
        res[key.lower()] = d[key]
    return res

def fuzzy_get(_dict, aliases, default):
    """
    get a value from a list of keys(aliases), 
    return first value which it's key exist in dict,
    if no keys found, return default.
    """
    for name in aliases:
        if name in _dict:
            return _dict[name]
    else:
        return default


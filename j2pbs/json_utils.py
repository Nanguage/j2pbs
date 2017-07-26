from .exceptions import ConfFileSyntaxError

"""
json_utils
~~~~~~~~~~
These functions for processing json dict,
such as upper and lower dict keys and extract specific field from dict.

"""

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


def extract_dir(js_dict, default_dir):
    aliases = ('DIR', 'DIRECTORY', 'FLODER', 'PATH')
    _dir = fuzzy_get(js_dict, aliases, default_dir)
    return _dir


def extract_queue(js_dict, default_queue):
    aliases = ('QUEUE', 'Q')
    queue = fuzzy_get(js_dict, aliases, default_queue)
    return queue


def extract_resources(js_dict, default_resources):
    aliases = ('RES', 'RESOURCES', 'RESOURCE')
    resources = fuzzy_get(js_dict, aliases, default_resources)
    return resources


def extract_scope(js_dict):
    aliases = ('VAR', 'VARS', 'VARIABLE')
    scope = fuzzy_get(js_dict, aliases, {})
    if type(scope) != dict:
        raise ConfFileSyntaxError("VAR is must a object/dict.")
    return scope


def extract_commands(job_dict):
    aliases = ('CMD', 'CMDS', 'COMMAND', 'COMMANDS')
    commands = fuzzy_get(job_dict, aliases, [])
    if type(commands) is not list:
        commands = [commands]
    if commands == []:
        raise ConfFileSyntaxError("Job node must contain no empty COMMAND or COMMANDS field.")
    return commands


def extract_dependent(job_dict):
    aliases = ('DEPEND', 'DEPENDENT', 'DEPENDENCE', 'DEPENDENCES')
    dependent = fuzzy_get(job_dict, aliases, [])
    if type(dependent) is not list:
        dependent = [dependent]
    return dependent


def extract_jobs(graph_dict):
    aliases = ("JOB", "JOBS", "NODES")
    jobs = fuzzy_get(graph_dict, aliases, [])
    if type(jobs) != list:
        jobs = [jobs]
    if jobs == []:
        raise ConfFileSyntaxError("Graph at least contain one job.")
    return jobs

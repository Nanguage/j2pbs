from .utils import upper_dict_key, lower_dict_key
from .utils import fuzzy_get
from .exceptions import JsonSynaticError

class Job:
    """
    The abstraction of one PBS job.

    supported features:

        | id:    (int) job identifier
        | name:  (str) 
        | queue: (str) job queue [batch]
        | dir:   (str) working directory
        | resources:
        |     nodes: (int/str) nodes name or number [1]
        |     ppn:   (int) MPI processes per node [1]
        |     mem:   (str) memory
        |     walltime: (str)
        | dependences: (list)

        Not all, just some PBS features common use. :( 
        "id" is virtual id, for specify dependence relationship.

    """
    DEFAULT_RESOURCES = { 'nodes': 1, 'ppn': 1 }
    DEFAULT_QUEUE = 'batch'
    DEFAULT_DIR   = '$HOME'

    def __init__(self, job_dict, 
                 default_resources=DEFAULT_RESOURCES,
                 default_queue=DEFAULT_QUEUE,
                 default_dir=DEFAULT_DIR):
        job_dict = upper_dict_key(job_dict) # upper case all keys

        # parse ID and NAME
        try:
            self.id = job_dict['ID']
            self.name = job_dict['NAME']
        except KeyError:
            raise JsonSynaticError("Job node must contain ID and NAME fields.")

        self.dir = self.parse_dir(job_dict, default_dir)
        self.queue = self.parse_queue(job_dict, default_queue)
        self.commands  = self.parse_commands(job_dict)
        self.resources = self.parse_resources(job_dict, default_resources)
        self.dependent = self.parse_dependent(job_dict)

    @staticmethod
    def parse_dir(job_dict, default_dir):
        aliases = ('DIR', 'DIRECTORY', 'FLODER', 'PATH')
        _dir = fuzzy_get(job_dict, aliases, default_dir)
        return _dir

    @staticmethod
    def parse_queue(job_dict, default_queue):
        aliases = ('QUEUE', 'Q')
        queue = fuzzy_get(job_dict, aliases, default_queue)
        return queue

    @staticmethod
    def parse_commands(job_dict):
        aliases = ('CMD', 'CMDS', 'COMMAND', 'COMMANDS')
        commands = fuzzy_get(job_dict, aliases, [])
        if not hasattr(commands, '__iter__'):
            commands = [commands]
        if commands == []:
            raise JsonSynaticError("Job node must contain COMMAND or COMMANDS field.")
        return commands
    
    @staticmethod
    def parse_resources(job_dict, default_resources):
        aliases = ('RES', 'RESOURCES', 'RESOURCE')
        resources = fuzzy_get(job_dict, aliases, default_resources)
        return resources

    @staticmethod
    def parse_dependent(job_dict):
        aliases = ('DEPEND', 'DEPENDENT', 'DEPENDENCE', 'DEPENDENCES')
        dependent = fuzzy_get(job_dict, aliases, [])
        if not hasattr(dependent, '__iter__'):
            dependent = [dependent]
        return dependent

    def to_script(self):
        """
        convert to pbs script string.
        """
        header_name = "#PBS -N {}".format(self.name)
        content = "\n".join(self.commands)

        # construct script string
        script = ""
        script += header_name + "\n"
        return script

    def __str__(self):
        return self.to_script()


class Graph:
    """
    The abstraction of pbs jobs relationship graph. 
    """
    def __init__(self, graph_dict):
        pass


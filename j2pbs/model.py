import os
import uuid
import shlex

from .utils import upper_dict_key, lower_dict_key
from .utils import fuzzy_get
from .exceptions import ConfFileSyntaxError, VariableKeyError, GraphLoopDependent, RepeatJobNameOrId

SHELL_SCOPE = os.environ

class Job:
    """
    The abstraction of one PBS job.

    supported PBS features:

        | id:    (int) job identifier
        | name:  (str) 
        | queue: (str) job queue [batch]
        | dir:   (str) working directory [$HOME]
        | resources:
        |     nodes: (int/str) nodes name or number [1]
        |     ppn:   (int) MPI processes per node [1]
        |     mem:   (str) memory
        |     walltime: (str)
        | dependences: (list) only supprt "afterok" type

        Not all, just some PBS features common use. :( 
        "id" is virtual id, for specify dependence relationship.

    class variable like RESOURCES, QUEUE ... control the job default parameters. 

    points about variable support implemention:
        1. supported the shell variable, 
           'SHELL' control use it or not in default condition.
        2. priority of variables: LOCAL > GLOBAL > SHELL


    """
    RESOURCES = { 'nodes': 1, 'ppn': 1 }
    QUEUE = 'batch'
    DIR   = SHELL_SCOPE['HOME']
    SHELL = False

    def __init__(self, job_dict, 
                 var_sub=True,
                 global_scope={}):
        job_dict = upper_dict_key(job_dict) # upper case all keys

        # extract ID and NAME
        try:
            self.id = job_dict['ID']
            self.name = job_dict['NAME']
        except KeyError:
            raise ConfFileSyntaxError("Job node must contain ID and NAME fields.")

        self.dir       = self.extract_dir(job_dict, self.DIR)
        self.queue     = self.extract_queue(job_dict, self.QUEUE)
        self.commands  = self.extract_commands(job_dict)
        self.resources = self.extract_resources(job_dict, self.RESOURCES)
        self.dependent = self.extract_dependent(job_dict)

        # construct scopes
        self.local_scope = self.extract_local_scope(job_dict)
        self.global_scope = global_scope

        shell = job_dict.get('SHELL', self.SHELL)
        if shell == 0: # 0 count as False
            shell = False
        elif type(shell) == str: 
            if shell.lower() == 'false': # 'flase' string count as False
                shell = False

        self.scope = {}
        if shell: 
            self.scope.update(SHELL_SCOPE) # priority: shell < global < local
        self.scope.update()
        self.scope.update(self.local_scope)

        if var_sub: # variable subsititute
            self.var_sub()

    @staticmethod
    def extract_dir(job_dict, default_dir):
        aliases = ('DIR', 'DIRECTORY', 'FLODER', 'PATH')
        _dir = fuzzy_get(job_dict, aliases, default_dir)
        return _dir

    @staticmethod
    def extract_queue(job_dict, default_queue):
        aliases = ('QUEUE', 'Q')
        queue = fuzzy_get(job_dict, aliases, default_queue)
        return queue

    @staticmethod
    def extract_commands(job_dict):
        aliases = ('CMD', 'CMDS', 'COMMAND', 'COMMANDS')
        commands = fuzzy_get(job_dict, aliases, [])
        if type(commands) is not list:
            commands = [commands]
        if commands == []:
            raise ConfFileSyntaxError("Job node must contain no empty COMMAND or COMMANDS field.")
        return commands
    
    @staticmethod
    def extract_resources(job_dict, default_resources):
        aliases = ('RES', 'RESOURCES', 'RESOURCE')
        resources = fuzzy_get(job_dict, aliases, default_resources)
        return resources

    @staticmethod
    def extract_dependent(job_dict):
        aliases = ('DEPEND', 'DEPENDENT', 'DEPENDENCE', 'DEPENDENCES')
        dependent = fuzzy_get(job_dict, aliases, [])
        if type(dependent) is not list:
            dependent = [dependent]
        return dependent

    @staticmethod
    def extract_local_scope(job_dict):
        aliases = ('VAR', 'VARS', 'VARIABLE')
        local_scope = fuzzy_get(job_dict, aliases, {})
        if type(local_scope) != dict:
            raise ConfFileSyntaxError("VAR is must a object/dict.")
        return local_scope

    def to_script(self):
        """
        convert to pbs script string.
        """
        header_name = "#PBS -N {}".format(self.name)
        header_queue = "#PBS -q {}".format(self.queue)
        header_dir = "#PBS -d {}".format(self.dir)

        # generate resource header
        header_resource = ""
        if ('nodes' in self.resources) and ('ppn' in self.resources):
            nodes, ppn = self.resources['nodes'], self.resources['ppn']
            header_resource += "#PBS -l nodes={}:ppn={}\n".format(nodes, ppn)
            self.resources = self.resources.copy() # if not copy, will change the class variable: RESOURCES
            del self.resources['nodes']
            del self.resources['ppn']
        elif ('ppn' in self.resources) and ('nodes' not in self.resources):
            raise ConfFileSyntaxError("Resources can't only contain ppn without nodes")
        for k, v in self.resources.items():
            header_resource += "#PBS -l {}={}\n".format(k, v)

        content = "\n".join(self.commands)

        # construct script string
        script = ""
        script += header_name + "\n"
        script += header_dir + "\n"
        script += header_queue + "\n"
        script += header_resource
        script += content

        return script

    def var_sub(self, scope=None, var_sign='$', escape="^"):
        """
        variable substitution, 
        substitute commands's variable token with variables in scope.

        :scope: variables used to subsititute command. [self.scope]
        :var_sign: the start char of a variable. ['$']
        :escape: the escape char. ['\\']

        """
        if not scope:
            scope = self.scope
        for i, cmd in enumerate(self.commands):
            args = shlex.split(cmd, comments="#") # split command to arguments
            for j, arg in enumerate(args):
                if arg.startswith(escape):
                    args[j] = arg[1:]
                    continue
                if arg.startswith(var_sign): # this argument is a variable
                    var_key = arg[1:]
                    if var_key not in scope:
                        raise VariableKeyError("Variable {} not found.".format(var_key))
                    var = scope[var_key]
                    args[j] = var
            subed = " ".join(args)
            self.commands[i] = subed

    def __str__(self):
        return self.to_script()


class Graph:
    """
    The abstraction of pbs jobs relationship graph. 
    """
    def __init__(self, graph_dict):
        graph_dict = upper_dict_key(graph_dict)

        name = graph_dict.get('NAME', None)
        if not name:
            name = uuid.uuid4().hex[:8] # default name is an unique id
        self.name = name

        self.jobs = self.extract_jobs(graph_dict)
        self.init_jobs() # init job objects
        self.check_jobs()
        self.parse_dependent()

    @staticmethod
    def extract_jobs(graph_dict):
        aliases = ("JOB", "JOBS", "NODES")
        jobs = fuzzy_get(graph_dict, aliases, [])
        if type(jobs) != list:
            jobs = [jobs]
        if jobs == []:
            raise ConfFileSyntaxError("Graph at least contain one job.")
        return jobs

    def init_jobs(self):
        """ init jobs, convert json dicts to Job object. """
        for i, js_dict in enumerate(self.jobs):
            self.jobs[i] = Job(js_dict)

    def parse_dependent(self):
        """ fetch all jobs dependent store in self.dependent """
        id2job = {job.id:job for job in self.jobs}
        self.dependent = {}
        for job in self.jobs:
            ids = job.dependent
            self.dependent[job] = [id2job[_id] for _id in ids]

    def check_jobs(self):
        """ jobs validity check. """
        # check if there is repeated job's name and id
        ids = set()
        names = set()
        for job in self.jobs:
            if job.id in ids:
                raise RepeatJobNameOrId(type_='id')
            if job.name in names:
                raise RepeatJobNameOrId(type_='name')
            ids.add(job.id)
            names.add(job.name)

    @property
    def job_scripts(self):
        """ 
        convert jobs to scripts,
        return a dict mapping job id to script
        """
        id2script = {}
        for job in self.jobs:
            id_ = job.id
            script = job.to_script()
            id2script[id_] = script
        return id2script

    @property
    def control_script(self):
        """ 
        create a script control all jobs,
        ensure them run according the dependent relation ship. 
        
        the control script will look like this:
        
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #!/bin/bash

        JOB1_SCR=$(cat <<'EOF'
            #PBS -N job1
            #PBS -l nodes=1:ppn=1

            sleep 10
        EOF
        )

        JOB2_SCR=$(cat <<'EOF'
            #PBS -N job2 
            #PBS -l nodes=1:ppn=1

            echo "Hello!"
        EOF
        )

        JOB1_ID=$(echo "$JOB1_SCR" | qsub)
        echo $JOB1_ID
        JOB2_ID=$(echo "$JOB2_SCR" | qsub -w afterok:$JOB1_ID)
        echo $JOB2_ID
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        """
        ctrl_scr = ""
        shebang = "#!/bin/bash"
        ctrl_scr += (shebang + "\n\n")

        def job_assign_state(job):
            """ return an bash assignment statement, store job script to a variable. """
            state = "{}_SCR=$(cat <<'EOF'\n{}\nEOF\n)".format(job.name.upper(), job.to_script())
            return state
                    

        for job in self.jobs:
            ctrl_scr += job_assign_state(job)
            ctrl_scr += "\n"
        ctrl_scr += "\n"

        status = {job: False for job in self.jobs} # status indicate it is converted or not

        def is_solved(job):
            """ the dependent of job is solved or not. """
            return all([status[j] for j in self.dependent[job]])

        def qsub_and_fetch_state(job, depend_type="afterok"):
            """ return an statement, submit the job and fetch job id. """
            dependent_jobs = self.dependent[job]
            if dependent_jobs == []:
                state = "{}_ID=$(echo \"${}_SCR\" | qsub)".format(
                        job.name.upper(), job.name.upper())
            else:
                depend_job_names = [j.name.upper() + "_ID" for j in dependent_jobs]
                depends = [depend_type + ":" + "$" + name for name in depend_job_names]
                depends = ",".join(depends)
                state = "{}_ID=$(echo \"${}_SCR\" | qsub -W depend={})".format(
                        job.name.upper(), job.name.upper(), depends)
            return state

        # dependence solving loop 
        n = 0
        while not all(status.values()):
            n += 1
            for job in self.jobs:
                if is_solved(job):
                    ctrl_scr += (qsub_and_fetch_state(job) + "\n")
                    ctrl_scr += ("echo ${}".format(job.name.upper() + "_ID") + "\n")
                    ctrl_scr += "\n"
                    status[job] = True
            if n >= len(self.jobs):
                raise GraphLoopDependent()

        return ctrl_scr

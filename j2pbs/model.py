import os
import uuid
import shlex

from .json_utils import upper_dict_key, lower_dict_key
from .json_utils import extract_dir, extract_queue, extract_resources, extract_scope
from .json_utils import extract_commands, extract_dependent
from .json_utils import extract_jobs
from .exceptions import ConfFileSyntaxError, GraphLoopDependent, RepeatJobNameOrId
from .semantic import var_sub

# defaults
SHELL_SCOPE = os.environ
RESOURCES = {'nodes': 1, 'ppn': 1}
QUEUE = 'batch'
DIR   = "$PWD"
SHELL = False

class Job:
    """
    The abstraction of one PBS job.

    Supported PBS features:

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

    Class variable like RESOURCES, QUEUE ... control the job default parameters. 

    Points about variable support implemention:
        1. supported the shell variable, 
           'SHELL' control use it or not in default condition.
        2. priority of variables: LOCAL > GLOBAL > SHELL

    Init a Job:
    >>> js_dict = json.loads(json_str)
    >>> job = Job(js_dict)

    convert it to pbs script:
    >>> print(job.pbs_script)
    ...

    """

    def __init__(self, job_dict, 
                 cmd_sub=True,
                 global_scope={},
                 default_dir=DIR,
                 default_queue=QUEUE,
                 default_resources=RESOURCES,
                 default_shell=SHELL):
        job_dict = upper_dict_key(job_dict) # upper case all keys

        # extract ID and NAME
        try:
            self.id = job_dict['ID']
            self.name = job_dict['NAME']
            self.name = self.name.replace(" ", "_") # replace space with under score.
        except KeyError:
            raise ConfFileSyntaxError("Job node must contain ID and NAME fields.")

        self.dir       = extract_dir(job_dict, default_dir)
        self.queue     = extract_queue(job_dict, default_queue)
        self.commands  = extract_commands(job_dict)
        self.resources = extract_resources(job_dict, default_resources)
        self.dependent = extract_dependent(job_dict)

        # construct scopes
        self.local_scope = extract_scope(job_dict)
        self.global_scope = global_scope

        shell = job_dict.get('SHELL', default_shell)
        if shell == 0: # 0 count as False
            shell = False
        elif type(shell) == str: 
            if shell.lower() == 'false': # 'flase' string count as False
                shell = False

        self.scope = {}
        if shell: 
            self.scope.update(SHELL_SCOPE) # priority: shell < global < local
        self.scope.update(self.global_scope)
        self.scope.update(self.local_scope)

        if cmd_sub: # variable subsititute
            self.cmd_sub()
        self.dir_sub()

    @property
    def pbs_script(self):
        """ Convert to pbs script string. """
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

    def cmd_sub(self, scope=None, comment="*"):
        """
        Variable substitution, 
        substitute commands's variable token with variables in scope.
        """
        if not scope:
            scope = self.scope
        for i, cmd in enumerate(self.commands):
            args = shlex.split(cmd, comments=comment) # split command to arguments
            subed_args = var_sub(args, scope, var_sign='$', escape="^")
            subed = " ".join(subed_args)
            self.commands[i] = subed

    def dir_sub(self):
        """
        Do variable substitution in 'dir' with shell scope and self scope.
        priority: self.scope > shell scope
        """
        scope = {}
        scope.update(SHELL_SCOPE)
        scope.update(self.scope)
        args = [self.dir]
        subed_args = var_sub(args, scope, var_sign='$', escape="^")
        self.dir = subed_args[0] 

    def __str__(self):
        return self.pbs_script


class Graph:
    """
    The abstraction of pbs jobs relationship graph. 
    Convert the json dict to the control script,
    according to the dependent relationship between jobs.

    In the same time it also provide the global varibles scope, 
    and the default settings for Jobs.

    Init graph with a json dict:
    >>> js_dict = json.loads(json_str)
    >>> g = Graph(js_dict)

    get the control scipt converted from Graph:
    >>> print(g.control_script)
    ...

    """

    def __init__(self, graph_dict):
        graph_dict = upper_dict_key(graph_dict)

        name = graph_dict.get('NAME', None)
        if not name:
            name = uuid.uuid4().hex[:8] # default name is an unique id
        self.name = name

        # extract job default properties
        self.job_default_dir = extract_dir(graph_dict, None) or DIR
        self.job_default_queue = extract_queue(graph_dict, None) or QUEUE
        self.job_default_resources = extract_resources(graph_dict, None) or RESOURCES
        self.job_default_shell = graph_dict.get('SHELL', None) or SHELL
        # extract graph scopy(job global scopy)
        self.scope = extract_scope(graph_dict)

        self.jobs = extract_jobs(graph_dict)
        self.init_jobs() # init job objects
        self.check_jobs()
        self.parse_dependent()

    def init_jobs(self):
        """ init jobs, convert json dicts to Job object. """
        for i, js_dict in enumerate(self.jobs):
            self.jobs[i] = Job(
                    js_dict,
                    global_scope=self.scope,
                    default_dir=self.job_default_dir,
                    default_queue=self.job_default_queue,
                    default_resources=self.job_default_resources,
                    default_shell=self.job_default_shell)

    def parse_dependent(self):
        """ Fetch all jobs dependent store in self.dependent. """
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
        Convert jobs to scripts,
        return a dict mapping job id to script
        """
        id2script = {}
        for job in self.jobs:
            id_ = job.id
            script = job.pbs_script
            id2script[id_] = script
        return id2script

    @property
    def control_script(self):
        """ 
        Create a script control all jobs,
        ensure them run according the dependent relation ship. 
        
        The control script will look like this:
        
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
            """ 
            return an bash assignment statement, store job script to a variable. 
            like:
                JOB2_SCR=$(cat <<'EOF'
                    #PBS -N job2 
                    #PBS -l nodes=1:ppn=1

                    echo "Hello!"
                EOF
                )
            """
            state = "{}_SCR=$(cat <<'EOF'\n{}\nEOF\n)".format(job.name.upper(), job.pbs_script)
            return state
                    

        for job in self.jobs:
            ctrl_scr += job_assign_state(job)
            ctrl_scr += "\n"
        ctrl_scr += "\n"

        status = {job: False for job in self.jobs} # status indicate it is converted or not

        def is_solved(job):
            """ The dependent of job is solved or not. """
            return all([status[j] for j in self.dependent[job]])

        def qsub_and_fetch_state(job, depend_type="afterok"):
            """ 
            Return an statement, submit the job and fetch job id,
            like:
                "JOB2_ID=$(echo "$JOB2_SCR" | qsub -w afterok:$JOB1_ID)"
            """
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

    def __str__(self):
        return self.control_script

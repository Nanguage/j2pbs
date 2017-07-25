import json

from j2pbs.model import Job
from j2pbs.exceptions import ConfFileSyntaxError, VariableKeyError

def print_job(job):
    print(
            "id:{}\n" "name:{}\n"
            "queue:{}\n"
            "dir:{}\n"
            "commands:{}\n"
            "resources:{}\n"
            "dependent:{}".format(
                job.id,
                job.name,
                job.queue,
                job.dir,
                job.commands,
                job.resources,
                job.dependent,
            )
       )
    print("\"\"\"\n{}\n\"\"\"".format(job.to_script()))


if __name__ == "__main__":

    job_json = """
    {
        "id": 0,
        "name": "test",
        "resources": {"nodes": 1, "ppn": 10, "walltime": "10:10:10"},
        "cmd": "echo 1"
    }
    """
    
    job_dict = json.loads(job_json)
    job = Job(job_dict)
    print_job(job)
    print()
    
    job_json = """
    {
        "id": 1,
        "name": "test2",
        "cmd": "echo 1"
    }
    """
    job_dict = json.loads(job_json)
    job = Job(job_dict)
    print_job(job)
    print()
    
    
    # missing id
    job_json = """
    {
        "name": "test2",
        "cmd": "echo 1"
    }
    """
    job_dict = json.loads(job_json)
    try:
        job = Job(job_dict)
    except ConfFileSyntaxError as e:
        print(str(e))
    print()
    
    # missing command
    job_json = """
    {
        "id": 3,
        "name": "test2"
    }
    """
    job_dict = json.loads(job_json)
    try:
        job = Job(job_dict)
    except ConfFileSyntaxError as e:
        print(str(e))
    print()
    
    # test varible
    job_json = """
    {
        "id": 4,
        "name": "test",
        "shell": true,
        "var": { "name": "alice" },
        "cmd": ["echo $HOME", "echo hello $name"]
    }
    """
    job_dict = json.loads(job_json)
    job = Job(job_dict)
    print_job(job)
    print()

    # test varible, without shell
    job_json = """
    {
        "id": 5,
        "name": "test",
        "shell": false,
        "var": { "name": "alice" },
        "cmd": ["echo $HOME", "echo hello $name"]
    }
    """
    job_dict = json.loads(job_json)
    try:
        job = Job(job_dict)
    except VariableKeyError as e:
        print(str(e))
    print()

    # test varible, escape
    job_json = """
    {
        "id": 6,
        "name": "test",
        "shell": false,
        "var": { "name": "alice" },
        "cmd": ["echo ^$HOME", "echo hello $name"]
    }
    """
    job_dict = json.loads(job_json)
    job = Job(job_dict)
    print_job(job)
    print()

    # test default behavior
    job_json = """
    {
        "id": 7,
        "name": "test",
        "shell": true,
        "var": { "name": "alice" },
        "cmd": ["echo $HOME", "echo hello $name"]
    }
    """
    Job.RESOURCES = {'nodes':1, 'ppn':2}
    job_dict = json.loads(job_json)
    job = Job(job_dict)
    assert job.resources['nodes'] == 1
    assert job.resources['ppn'] == 2
    print_job(job)
    print()

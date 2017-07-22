import json

from j2pbs.model import Job
from j2pbs.exceptions import JsonSynaticError

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

job_json = """{
    "id": 0,
    "name": "test",
    "resources": {"nodes": 1, "ppn": 10},
    "cmd": "echo 1"
}
"""

job_dict = json.loads(job_json)
job = Job(job_dict)
print_job(job)
print()

job_json = """{
    "id": 2,
    "name": "test2",
    "cmd": "echo 1"
}
"""
job_dict = json.loads(job_json)
job = Job(job_dict)
print_job(job)
print()


job_json = """{
    "name": "test2",
    "cmd": "echo 1"
}
"""
job_dict = json.loads(job_json)
try:
    job = Job(job_dict)
except JsonSynaticError as e:
    print(str(e))
print()

job_json = """{
    "id": 3,
    "name": "test2"
}
"""
job_dict = json.loads(job_json)
try:
    job = Job(job_dict)
except JsonSynaticError as e:
    print(str(e))

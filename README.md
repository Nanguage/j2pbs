# j2pbs ---- Write pbs jobs in JSON format.


[JSON](http://www.json.org/) is a simple and readble file format
for data transfer and configuration.
What if we using it organize our 
PBS([Portable Batch System](https://en.wikipedia.org/wiki/Portable_Batch_System)) jobs?
Maybe this will make it easier to submit and manage our PBS jobs.
j2pbs is a python package and command line tools help you doing such things.

## Installation
```
pip install j2pbs
```

## Example:

Firstly, we begin with a very simple example:

Here, we want submit two job, the first job is just `sleep 10` seconds,
and the second one just `echo Hi!`,
the second job is depend on the first,
it means that the second job begin to run when the first job terminate normally.
We can express these two jobs like following json file:
```
{
    "name": "simple example",
    "jobs": 
     [
        { "id": 0, "name": "job1", "cmd": "sleep 10" },
        { "id": 1, "name": "job2", "cmd": "echo Hi!", "depend": 0 }
     ]
}
```

Assume we store this in the file "simple.json".
Next, we can submit these jobs using the command line interface:
```
$ python -m j2pbs submit simple.json
```
Actually, we can break this down to two single steps, it has same effect:
```
$ # first convert the json config file to one control bash script.
$ python -m j2pbs convert simple.json simple.sh
$ # then run the control script
$ bash simple.sh
```

## Features:
### 1. variables suport
#### 1.1 Job level variables
For example:
```
{
    "id": 0,
    "name": "var_test",
    "var": {"greet": "Hello World!"},
    "cmd": "echo $greet"
}
```
It's pbs job will output "Hello World!" to stdout.

#### 1.2 Global level variables
```
{
    "name": "var_test",

    "var":
    {
        "person1": "Alice",    
        "person2": "Bob"
    },

    "jobs": 
     [ 
        { "id": 0, "name": "hello1", "cmd": "echo Hi $person1" },
        { "id": 1, "name": "hello2", "cmd": "echo Hi $person2" }
     ]
}
```

#### 1.3 Shell variables
```
{
    "name": "var_test",
}
```

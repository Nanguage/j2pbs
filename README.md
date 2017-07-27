# j2pbs ---- Write pbs jobs in JSON format.


[JSON](http://www.json.org/) is a simple and readble file format
for data transfer and configuration.
What if we using it organize our 
PBS([Portable Batch System](https://en.wikipedia.org/wiki/Portable_Batch_System)) jobs?
Maybe this will make it easier to submit and manage our PBS jobs.
j2pbs is a python package and command line tools help you doing such things.


## Example:

A simple example:
```

```


## TODO LIST

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

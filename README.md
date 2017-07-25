# j2pbs ---- Write pbs jobs in json format.

## Example:


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

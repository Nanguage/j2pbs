from __future__ import print_function

import json

from j2pbs.model import Graph
from j2pbs.exceptions import GraphLoopDependent, RepeatJobNameOrId

def get_graph(js_str):
    js_dict = json.loads(js_str)
    return Graph(js_dict)

file_spliter = "*" * 50

if __name__ == "__main__":
    js_str = """
    {
        "name": "test",
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":1, "name":"test2", "cmd":"echo hello", "depend": 0}
        ]
    }
    """
    g0 = get_graph(js_str) 
    print(file_spliter)
    print(g0.control_script)
    print(file_spliter)
    print()

    # loop dependent condition
    js_str = """
    {
        "name": "test",
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10", "depend": 1},
            {"id":1, "name":"test2", "cmd":"echo hello", "depend": 0}
        ]
    }
    """
    g0 = get_graph(js_str) 
    try:
        print(g0.control_script)
    except GraphLoopDependent as e:
        print(str(e))

    # repeat id and name condition
    js_str = """
    {
        "name": "test",
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":0, "name":"test2", "cmd":"echo hello"}
        ]
    }
    """
    try:
        g0 = get_graph(js_str) 
        print(g0.control_script)
    except RepeatJobNameOrId as e:
        print(str(e))

    js_str = """
    {
        "name": "test",
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":1, "name":"test1", "cmd":"echo hello"}
        ]
    }
    """
    try:
        g0 = get_graph(js_str) 
        print(g0.control_script)
    except RepeatJobNameOrId as e:
        print(str(e))

    # more complex condiction
    #   
    #    1--->         --->4
    #         \       /
    #          2---->3
    #         /       \
    #    0--->         --->5
    #
    js_str = """
    {
        "name": "be sunk in sleep",
        "jobs": 
        [
            {"id":0, "name":"test0", "cmd":"sleep 10"},
            {"id":1, "name":"test1", "cmd":"sleep 10"},
            {"id":2, "name":"test2", "cmd":"sleep 20", "depend":[0, 1]},
            {"id":3, "name":"test3", "cmd":"echo draming...; sleep 20", "depend":2},
            {"id":4, "name":"test4", "cmd":"sleep 20", "depend":3},
            {"id":5, "name":"test5", "cmd":"sleep 20", "depend":3}
        ]
    }
    """
    g1 = get_graph(js_str) 
    print(file_spliter)
    print(g1.control_script)
    print(file_spliter)
    print()

    # test global var
    js_str = """
    {
        "name": "test",
        "var": {"me":"alice", "you":"bob"},
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"echo hello $you"},
            {"id":1, "name":"test2", "cmd":"echo hello $me", "depend": 0}
        ]
    }
    """
    g2 = get_graph(js_str) 
    print(file_spliter)
    print(g2.control_script)
    print(file_spliter)
    print()

    # test control job default setting
    js_str = """
    {
        "name": "test",
        "queue": "big",
        "dir": "/home/nanguage/pbstmp",
        "resources": {"nodes":1, "ppn":2},
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":1, "name":"test2", "cmd":"echo hello", "depend": 0}
        ]
    }
    """
    g3 = get_graph(js_str) 
    print(file_spliter)
    print(g3.control_script)
    print(file_spliter)
    print()

    # test dir sub
    js_str = """
    {
        "name": "test",
        "queue": "big",
        "dir": "$HOME/pbstmp",
        "resources": {"nodes":1, "ppn":2},
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":1, "name":"test2", "cmd":"echo hello", "depend": 0}
        ]
    }
    """
    g4 = get_graph(js_str) 
    print(file_spliter)
    print(g4.control_script)
    print(file_spliter)
    print()

    js_str = """
    {
        "name": "test",
        "queue": "big",
        "dir": "$myhome/pbstmp",
        "resources": {"nodes":1, "ppn":2},
        "var":
        {
            "myhome": "/home/nanguage/PlayGround"
        },
        "jobs": 
        [
            {"id":0, "name":"test1", "cmd":"sleep 10"},
            {"id":1, "name":"test2", "cmd":"echo hello", "depend": 0}
        ]
    }
    """
    g5 = get_graph(js_str) 
    print(file_spliter)
    print(g5.control_script)
    print(file_spliter)
    print()

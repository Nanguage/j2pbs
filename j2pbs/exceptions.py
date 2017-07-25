class ConfFileSyntaxError(SyntaxError):
    """ Json config file syntax error. """
    pass

class VariableKeyError(KeyError):
    """ Variable not found in scope. """
    pass

class GraphLoopDependent(Exception):
    """ There are loop in dependent relationship. """
    def __init__(self):
        self.msg = 'There are loop in dependent relationship.'

    def __str__(self):
        return self.msg

class RepeatJobNameOrId(ConfFileSyntaxError):
    """ There are repeated job name or id. """
    def __init__(self, type_="id"):
        self.msg = "There are repeated job " + type_ + " in your config file."

    def __str__(self):
        return self.msg

from .exceptions import VariableKeyError

def var_sub(args, scope, var_sign='$', escape='^'):
    """
    Variable substitution, 
    substitute args's variable token with variables in scope.

    :args: an argument list to be substitute.
    :scope: variables used to subsititute command. [self.scope]
    :var_sign: the start char of a variable. ['$']
    :escape: the escape char. ['^']

    """
    def sub(token):
        if token.startswith(escape):
            subed = token[1:]
        elif token.startswith(var_sign): # this argument is a variable
            var_key = token[1:]
            if var_key not in scope:
                raise VariableKeyError("Variable '{}' not found.".format(var_key))
            subed = scope[var_key]
        else:
            subed = token
        return subed

    subed_args = []

    for arg in args:
        if "/" in arg:
            paths = arg.split("/") # split arg for sovling var sub within path
            for i, p in enumerate(paths):
                paths[i] = sub(p) 
            subed = "/".join(paths)
            subed_args.append(subed)
        else:
            subed_args.append(sub(arg))
    return subed_args

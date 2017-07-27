import subprocess

def here_doc(content):
    """ construct bash here doc. """
    here_doc = "<<'EOF'\n{}\nEOF\n".format(content)
    return here_doc


def qsub(script_str):
    """ submit script string using qsub command. """
    cmd = "(cat {}) | qsub".format(here_doc(script_str))
    subp = subprocess.Popen(cmd, shell=True)


def run_bash(filename):
    """ run bash script. """
    cmd = "cat {} | bash".format(filename)
    subp = subprocess.run(cmd, shell=True)

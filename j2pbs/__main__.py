import argparse
import sys
import json
import tempfile

from .model import Job, Graph
from .pbs_utils import qsub, run_bash


def argument_parser():
    parser = argparse.ArgumentParser(
            prog="j2pbs",
            description="Command line tools for manage pbs jobs with json file format.")

    parser.add_argument("--type", "-t",
            choices=["graph", "job"],
            default="graph",
            help="use to specify the type of json config file,"
            " 'graph' for jobs, 'job' for single job")

    subparsers = parser.add_subparsers(
            title="sub-commands",
            help="sub-command help")

    # "convert" sub command
    convert_parser = subparsers.add_parser("convert",
            help="convert json config file to a control shell script.")
    convert_parser.add_argument("json",
            type=argparse.FileType(mode='r'),
            help="config json file")
    convert_parser.add_argument("target",
            type=argparse.FileType(mode='w'),
            default=sys.stdout,
            nargs='?',
            help="target control script [stdout]")
    convert_parser.set_defaults(func=convert)

    # "submit" sub command
    submit_parser = subparsers.add_parser("submit",
            help="submit jobs which descripted in json config file.")
    submit_parser.add_argument("json",
            type=argparse.FileType(mode='r'),
            help="config json file")
    submit_parser.set_defaults(func=submit)
    return parser


def convert(args):
    """ Function for process 'convert' sub command. """
    with args.json as f:
        js_str = f.read()
    js_dict = json.loads(js_str)
    with args.target as f:
        if args.type == 'job':
            job = Job(js_dict)
            f.write(job.pbs_script)
        else:
            g = Graph(js_dict)
            f.write(g.control_script)


def submit(args):
    """ Function for process 'submit' sub command."""
    with args.json as f:
        js_str = f.read()
    js_dict = json.loads(js_str)
    if args.type == 'job':
        job = Job(js_dict)
        qsub(job.script_str)
    else:
        g = Graph(js_dict)
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(g.control_script)
            f.flush()
            run_bash(f.name)


def main():
    parser = argument_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import collections
import os
import re
import shlex
import subprocess
import sys


__version__ = '0.2'


# === everything we need from six ===
PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,
else:
    string_types = basestring,
# ===================================


# === Procfile parsing ===
# borrowed from honcho
# https://github.com/nickstenning/honcho/blob/f1b46387654544e6577a9748423ee22bd95c5f75/honcho/environ.py#L16
# https://github.com/nickstenning/honcho/blob/f1b46387654544e6577a9748423ee22bd95c5f75/honcho/environ.py#L52-L70
#
# Why not use the yaml parser? Because it interprets stuff it shouldn't. e.g
# web: echo "MYVAR: ${MYVAR}"
# Would cause yaml to throw a parse exception, although this is valid for a
# Procfile.
PROCFILE_LINE = re.compile(r'^([A-Za-z0-9_]+):\s*(.+)$')


class Procfile(object):
    """A data structure representing a Procfile"""

    def __init__(self):
        self.processes = collections.OrderedDict()

    def add_process(self, name, command):
        assert name not in self.processes, \
            "process names must be unique within a Procfile"
        self.processes[name] = command


def parse_procfile(contents):
    p = Procfile()
    for line in contents.splitlines():
        m = PROCFILE_LINE.match(line)
        if m:
            p.add_process(m.group(1), m.group(2))
    return p
# =======================


def expandvars(string, env=None):
    """
    Why this way of expanding environment vars is needed:
    os.path.expandvars() does not handle defaults ( ${MYVAR:-default} ) and also
    does not return an empty string for the case where the variable is not set.

    Instead of parsing them at all we *could* also run the whole command behind
    ['sh', '-c', command]
    That would naturally expand all the variables the way we want.
    But the problem with that is sh continues to run as the parent process and
    it will not forward Signals (like KILL) to the child process, causing
    orphaned processes all over the place if you try to kill this process.

    So we are using the default shell and echo itself to escape those pesky
    vars before executing the actual command.
    """
    env = env if env is not None else os.environ
    # prepare string for being used inside double quotes with printf or echo.
    string = (
        string
        .replace('\\', '\\\\')  # replace \ with \\
        .replace('"', '\\"')    # replace " with \"
    )
    return subprocess.check_output(
        ['sh', '-c', '''printf '%s' "{}"'''.format(string)], env=env)


def parse_command(command, env=None, expand=True):
    """
    takes a string or a list of args and returns a list of args where any
    shell style environment variables have been expanded.
    """
    env = env if env is not None else os.environ
    if isinstance(command, string_types):
        command = shlex.split(command)
    if expand:
        command = [expandvars(arg, env=env) for arg in command]
    return command


def cli():
    command_name = sys.argv[1]
    extra_args = sys.argv[2:]

    cwd_path = os.path.join(os.getcwd(), 'Procfile')
    env_path = os.environ.get('PROCFILE_PATH')

    if os.path.exists(cwd_path):
        procfile_path = cwd_path
    elif env_path and os.path.exists(env_path):
        procfile_path = env_path
    else:
        sys.exit('no Procfile path defined')

    with open(procfile_path) as fh:
        command = parse_procfile(fh.read()).processes[command_name]

    command = parse_command(command, env=os.environ)
    os.execvpe(command[0], command + extra_args, os.environ)


if __name__ == "__main__":
    cli()

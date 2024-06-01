import logging
import os.path
import subprocess
import sys
from typing import Union

logger = logging.getLogger(__name__)


class ShellError(Exception):
    pass


def run_commands_from_dir(working_dir: str,
                          commands: list[list[str]],
                          timeouts: Union[list[int], int] = 30,
                          stdout=sys.stdout) -> bool:

    count: int = len(commands)

    if isinstance(timeouts, int):
        timeouts = [timeouts] * count

    cwd = os.getcwd()
    try:
        __cd(working_dir)
        for i in range(count):
            success = run_command(commands[i], timeouts[i], stdout).returncode == 0
            if not success:
                return False
        return True
    finally:
        __cd(cwd)


def run_script(script_location: str, args: [str], timeout=30, stdout=sys.stdout) \
        -> Union[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess]:
    if not os.path.exists(script_location):
        raise ValueError(f"Script location does not exist: {script_location}")
    if not os.path.isfile(script_location):
        raise ValueError(f"Script location is not a file: {script_location}")

    has_access = grant_execute_permission_if_need(script_location)
    if not has_access:
        raise ShellError(f"Could not obtain execute permission for: {script_location}")

    script_dir, script_name = os.path.split(script_location)

    cwd = os.getcwd()

    try:
        __cd(script_dir)

        commands: [str] = [f'./{script_name}']

        commands.extend(args)

        return run_command(commands, timeout, stdout)
    finally:
        __cd(cwd)


def run_command(command: [str], timeout=30, stdout=sys.stdout) \
        -> Union[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess]:
    command = ' '.join(command)

    ps = execute_command(command, timeout, stdout)

    if stdout == subprocess.PIPE:
        line = '=' * 67
        logger.debug(f'shell log\n{line}\n% {command}\n{ps.stdout.strip()}\n{line}')

    if ps.returncode != 0:
        error_message = ps.stderr.strip()
        raise ShellError(f"Error running command: {command}.\n{error_message}")

    return ps


def execute_command(command: str, timeout=30, stdout=sys.stdout) \
        -> Union[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess]:

    logger.debug(f"Will execute command: {command}")

    return subprocess.run(
        command, shell=True, check=False, timeout=timeout,
        stderr=subprocess.PIPE, stdout=stdout, text=True)


def grant_execute_permission_if_need(script_location: str) -> bool:
    script_dir, script_name = os.path.split(script_location)

    cwd = os.getcwd()

    try:
        __cd(script_dir)

        if not os.access(script_name, os.X_OK):
            return run_command(['chmod', 'u+x', f'./{script_name}']).returncode == 0
        else:
            return True
    finally:
        __cd(cwd)


def __cd(target_dir: str):
    if not os.path.exists(target_dir):
        raise ValueError(f"Does not exist: {target_dir}")
    if not os.path.isdir(target_dir):
        raise ValueError(f"Not a directory: {target_dir}")
    os.chdir(target_dir)
    logger.debug(f"Changed dir to: {target_dir}")

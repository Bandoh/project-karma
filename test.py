import subprocess


def terminal_access(command: str):  # Changed from cmd: list to command: str
    """Execute terminal/shell commands on the operating system.

    **Use this tool for ANY system command, shell operation, or file system interaction.**

    Common commands that MUST use this tool:
    - ls, dir, pwd (directory operations)
    - cat, head, tail, grep (file reading)
    - mkdir, rm, cp, mv (file operations)
    - python, node, bash (running scripts)
    - Any command you would type in a terminal

    Args:
        command: The command as a string (e.g., "ls -la" or "cat file.txt")

    Returns:
        Command output. Returns stderr if errors occur, otherwise stdout.

    Examples:
        - "ls -la" - List directory contents
        - "cat file.txt" - Read file contents
        - "python --version" - Check Python version
        - "pwd" - Print working directory
    """
    print("In tool, this is the command:", command)

    # Split the command string into a list for subprocess
    cmd_list = command.split()
    print(cmd_list)
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.stderr:
        return result.stderr
    else:
        return result.stdout


print(terminal_access("ls app"))

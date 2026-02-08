import os
import subprocess

from google.genai import types

# Define run_python_file schema for LLM
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs specified python file in a path relative to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to specific python file relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Array of optional arguments (default is none)",
                items=types.Schema(
                    type=types.Type.STRING,
                ),
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=None):
    file_name, file_extension = os.path.splitext(file_path)

    if file_extension != ".py":
        return f'Error: "{file_path}" is not a Python file'

    try:
        # get absolute path of working directory
        absolute_path = os.path.abspath(working_directory)
    except Exception:
        return "Error: Invalid working directory"
    try:
        # get normalized, joined path of absolute path and directory
        target_path = os.path.normpath(os.path.join(absolute_path, file_path))
    except Exception:
        return "Error: Invalid directory"
    try:
        # check if target directory is in the absolute path
        valid_path = os.path.commonpath([absolute_path, target_path]) == absolute_path
    except Exception:
        return "Error: No common path found"

    # Safeguards to prevent LLM from running amok in system
    if not valid_path:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_path):
        return f'Error:  "{file_path}" does not exist or is not a regular file'

    #    try:
    #        dir_name, file_name = file_path.split("/")
    #        parent_directory = os.path.join(working_directory, dir_name)
    #        target_file = os.path.join(parent_directory, file_name)

    #    except ValueError:
    #        parent_directory = working_directory
    #        target_file = os.path.join(working_directory, file_path)

    # Build command to execute Python file
    command = ["python", target_path]
    if args:
        command.extend(args)

    # Execute Python file
    try:
        completed_process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.CalledProcessError as e:
        return f"Error: executing Python File {e}"
    if completed_process.returncode != 0:
        return f"Process exited with code {completed_process.returncode}"
    if not completed_process.stdout and not completed_process.stderr:
        return "No output produced"

    return f"STDOUT:{completed_process.stdout} STDERR: {completed_process.stderr}"

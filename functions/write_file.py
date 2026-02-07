import os

from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes text to a file in a path relative to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to specific python file relative to the working directory (default is the working directory itself)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to be written to the specified file",
            ),
        },
        required=["file_path", "content"],
    ),
)


def write_file(working_directory, file_path, content):
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
        return f"Error: Cannot read {file_path} as it is outside the permitted working directory"

    if os.path.isdir(target_path):
        return f"Error: Cannot write to {file_path} as it is a directory"
    try:
        dir_name, file_name = file_path.split("/")
        parent_directory = os.path.join(working_directory, dir_name)
        target_file = os.path.join(parent_directory, file_name)
    except ValueError:
        parent_directory = working_directory
        target_file = os.path.join(working_directory, file_path)

    try:
        os.makedirs(parent_directory, exist_ok=True)
        with open(target_file, "w") as f:
            f.write(content)
            return f"Successfully wrote to '{file_path}'({len(content)} characters written)"

    except FileNotFoundError:
        return f"Error: File not found or is not a regular file: '{file_path}'"

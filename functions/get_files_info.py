import os

from google.genai import types

# Define get_files_info schema for LLM
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    try:
        # get absolute path of working directory
        absolute_path = os.path.abspath(working_directory)
    except Exception:
        return "Error: Invalid working directory"
    try:
        # get normalized, joined path of absolute path and directory
        target_directory = os.path.normpath(os.path.join(absolute_path, directory))
    except Exception:
        return "Error: Invalid directory"
    try:
        # check if target directory is in the absolute path
        valid_path = (
            os.path.commonpath([absolute_path, target_directory]) == absolute_path
        )
    except Exception:
        return "Error: No common path found"

    # Safeguards to prevent LLM from running amok in system
    if not valid_path:
        return f"Error: Cannot list {directory} as it is outside the permitted working directory"

    if not directory:
        return f"Error: {directory} is not a directory"

    directory_contents = os.listdir(target_directory)

    file_info = []
    for item in directory_contents:
        item_path = os.path.join(target_directory, item)

        is_directory = os.path.isdir(item_path)
        file_size = os.path.getsize(item_path)
        file_info.append(
            f"- {item}: file_size={file_size} bytes, is_dir={is_directory}"
        )

    return "\n".join(file_info)

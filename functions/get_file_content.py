import os

from config import MAX_CHARS


def get_file_content(working_directory, file_path):
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

    try:
        with open(target_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)

            # After reading the first MAX_CHARS
            if f.read(1):
                file_content_string += (
                    f" [...File '{file_path}' truncated at {MAX_CHARS} characters]"
                )
    except FileNotFoundError:
        return f"Error: File not found or is not a regular file: '{file_path}'"

    return file_content_string

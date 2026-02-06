from functions.get_files_info import get_files_info

# Just tests the function locally without the LLM
print(get_files_info("calculator", "."))
print(get_files_info("calculator", "pkg"))
print(get_files_info("calculator", "/bin"))
print(get_files_info("calculator", "../"))

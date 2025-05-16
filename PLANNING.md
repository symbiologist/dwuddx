# Key Notes
-I am using VSCode and have created a venv in this project directory under .venv.
-I am using uv to manage my package dependencies. Please use uv to add dependencies when necessary (uv add).
-My API keys are stored via environment variables GEMINI_API_KEY and ANTHROPIC_API_KEY.
-Use pytest for unit tests. Please write unit tests in a manner that does NOT require importing the original scripts as modules.

-Here is the directory structure:
root/
├── input/
├── output/
├── src/
└── tests/

* `input/`: Directory is used to store any input data, files, or external resources
* `output/`: Directory is where results, generated files, or output data will be stored.
* `src/`: Directory where all scripts should be saved
* `tests/`: Directory is for test files for pytest

For all scripts, please name in order (first script should be 01_script, second should be 02_script, etc).
For any output that is generated as a result of a script, save the output in a subdirectory of `output` and name this subdirectory the name of the script (e.g., 02_script).

# Overarching Goals
The goal of this project is 

## Step-wise plan
Create a python script for each of the following tasks:
1.


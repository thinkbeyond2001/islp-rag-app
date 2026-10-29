# Installing with `venv` or `uv`

*AI Bootcamp: Generative AI and LLMs for Data Scientists*

This guide provides two alternatives to the course's default Conda setup. Choose either standard-library `venv` or `uv`; both create a repository-local environment named `.venv` and install the same Python packages used by the Conda environment.

Run all commands from the repository root.

## Option 1 - Standard-library `venv`

### Step 1 - Confirm that Python 3.10 is installed

On macOS or Linux:

```bash
python3.10 --version
```

On Windows PowerShell:

```powershell
py -3.10 --version
```

If the command fails, install Python 3.10 before continuing.

### Step 2 - Create and activate the environment

On macOS or Linux:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal prompt should include `(.venv)`.

### Step 3 - Install the course packages

```bash
python -m pip install --upgrade pip
python -m pip install -r 02_ds4b_301p_dev_langchain_latest_instructions/requirements_ds4b_301p_dev_langchain_latest.txt
python -m pip install -r additional-requirements.txt
```

## Option 2 - `uv`

`uv` can install Python and create the virtual environment as well as install the packages. If needed, install it by following the [official `uv` installation guide](https://docs.astral.sh/uv/getting-started/installation/), then confirm that it is available:

```bash
uv --version
```

### Step 1 - Create a Python 3.10 environment

```bash
uv venv --python 3.10 .venv
```

If Python 3.10 is not already available, `uv` downloads a compatible Python installation automatically.

### Step 2 - Install the course packages

`uv` automatically discovers the `.venv` directory, so activation is not required for installation:

```bash
uv pip install -r 02_ds4b_301p_dev_langchain_latest_instructions/requirements_ds4b_301p_dev_langchain_latest.txt
uv pip install -r additional-requirements.txt
```

Activate the environment before running course commands.

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Select the Environment in VS Code

1. Open the Command Palette with **Ctrl+Shift+P** on Windows/Linux or **Cmd+Shift+P** on macOS.
2. Run **Python: Select Interpreter**.
3. Select the interpreter in `.venv`.

If it is not listed, enter its path manually:

- macOS/Linux: `.venv/bin/python`
- Windows: `.venv\Scripts\python.exe`

## Verify the Installation

With the environment activated, run:

```bash
python --version
python -c "import chromadb, langchain, streamlit; print('Environment ready')"
```

The Python version should be 3.10 and the import command should print `Environment ready`.

Check for broken requirements with the command for your chosen installer:

```bash
# venv/pip
python -m pip check

# uv
uv pip check
```

The check should report no broken requirements.

## Install Future Course Requirements

When `additional-requirements.txt` changes, activate `.venv` and rerun the command for your chosen installer:

```bash
# venv/pip
python -m pip install -r additional-requirements.txt

# uv
uv pip install -r additional-requirements.txt
```

To leave either environment, run:

```bash
deactivate
```

## Quarto CLI

The Python requirements include the `quarto` package to match the Conda environment file. If you use course material that renders Quarto documents, also install the separate [Quarto CLI](https://quarto.org/docs/get-started/) and verify it with:

```bash
quarto check
```

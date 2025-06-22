

# Create virtual environment.
venv:
    uv venv --project .
    @echo "To activate the virtual environment, run: source .venv/bin/activate"

# Build package.
build:
    uv build

# Build package for development, exporting compile_commands.json
generate-compile-commands:
    # Use no-build-isolation, so that the include directories in `compile_commands.json`
    # are in the venv, rather than a temporary directory (as under build isolation).
    # TODO(nmusolino): use uv run --project . as part of script.
    uv build \
        --project . \
        --no-build-isolation \
        --config-setting cmake.define.MITER_COMPILE_COMMANDS_DIR="$(pwd)"

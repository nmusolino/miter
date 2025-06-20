

PROJECT_VENV := ".venv"

# Build package.
build:
    uv build

# Create virtual environment.
ensure-venv:
    uv venv

# Build package for development.
build-dev:  ensure-venv
    # Use no-build-isolation, so that the include directories in `compile_commands.json`
    # are in the venv, rather than a temporary directory (as under build isolation).
    # TODO(nmusolino): use uv run --project . as part of script.
    uv run --project . \
        uv build \
            --project . \
            --no-build-isolation \
            --config-setting cmake.define.MITER_COMPILE_COMMANDS_DIR="$(pwd)"

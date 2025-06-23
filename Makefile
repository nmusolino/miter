
.PHONY: build check docs format format-makefile generate-compile-commands help lint lint-makefile sdist sync uv-install-tools venv wheel

help:
	@echo "miter package development"
	@echo ""
	@echo "Available targets:"
	@sed -rn 's/^([a-zA-Z_-]+):.* ?## (.*)$$/"\1" "\2"/p' < $(MAKEFILE_LIST) | xargs printf "  make %-30s# %s\n"
	@echo ""

venv: ## Create virtual environment
	uv venv --project .
	@echo "To activate the virtual environment, run: source .venv/bin/activate"

sync: ## Update project environment
	uv sync

sdist: ## Build source distribution.
	uv build --sdist

wheel: ## Build Python wheel
	uv build --wheel

build: sdist wheel ## Build all.

generate-compile-commands: ## Export compile_commands.json
	# Use no-build-isolation, so that the include directories in `compile_commands.json`
	# are in the venv, rather than a temporary directory (as under build isolation).
	# TODO(nmusolino): use uv run --project . as part of script.
	uv build \
	--project . \
	--no-build-isolation \
		--config-setting cmake.define.MITER_COMPILE_COMMANDS_DIR="$(pwd)"

format-makefile:
	uv tool run mbake format Makefile

lint-makefile:
	uv tool run mbake format --check Makefile
	uv tool run mbake validate Makefile

format: format-makefile ## Format all sources

lint: lint-makefile ## Lint all sources

check: lint

docs: uv-install-docs-tools
	uv tool run --from sphinx \
		sphinx-build docs/ docs/output/
